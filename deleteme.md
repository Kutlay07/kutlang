Kanki, **#8'i hemen kapatmadan önce yaptığım inceleme sonucunda tablo netleşti.** GitHub'daki güncel `main` durumunu, #22'nin merge edilmiş halini, dört Sourcery finding'inin tamamının resolve edildiğini, policy/security/observability/execution boundary'lerini ve test/CI yapısını kontrol ettim. #22 gerçekten merge edilmiş durumda ve dört review thread'i de resolved.

## Önce verdict

**Safety & Control'ın temel mimarisi tamam.** #8'in DoD'si gerçekten karşılanmış görünüyor:

* workspace boundary
* risk classification
* trust level / safe defaults
* policy decision
* approval broker
* audit events + redaction
* process cancellation / timeout / process-tree cleanup

hepsi mevcut ve #8'in alt maddeleri tamamlanmış durumda.

Ama ben **#8'i şu an kapatmazdım.**

Çünkü incelemede **2 gerçek architectural cleanup** buldum. Bunlar speculative değil; #22 ile async tool execution eklenince mevcut contract'ların bir kısmı artık gerçeği temsil etmiyor.

---

# 1. En net problem: Tool contract'ları async gerçeğini yansıtmıyor

Şu an:

```python
ToolProvider.get_tools() -> list[SyncBaseTool]
```

diyor.

Ama `ExecutionToolProvider` artık şunları döndürüyor:

* `GetProcessOutputTool` → async
* `KillProcessTool` → async
* `RunBackgroundCommandTool` → async
* `RunCommandTool` → async

Yani provider contract'ı **yalan söylüyor**.

Aynı problem burada da var:

```python
ToolRegistration.tool: SyncBaseTool
ToolRegistry.get() -> SyncBaseTool
ToolRegistry.tools -> list[SyncBaseTool]
```

Ama runtime zaten bunun gerçek olmadığını kabul ediyor:

```text
if AsyncBaseTool:
    await tool.execute(...)
elif SyncBaseTool:
    tool.execute(...)
```

Yani runtime doğru davranıyor fakat **type boundary yanlış**.

### Doğru abstraction

Burada `BaseTool` tam olarak doğru ortak abstraction:

```text
                    BaseTool
                   /        \
          SyncBaseTool    AsyncBaseTool
               │                │
        filesystem tools    execution tools
```

`BaseTool` sadece metadata contract'ını taşıyor:

* `name`
* `description`
* `parameters`

Execution semantics ise alt contract'ta:

* sync → `SyncBaseTool`
* async → `AsyncBaseTool`

Bu mimari zaten kurulmuş. Sadece üst katmanlarda hâlâ `SyncBaseTool` yazıyor.

### Bu yüzden ilk cleanup'ımız

Şunların `BaseTool` kullanması gerekiyor:

```text
ToolProvider
ToolRegistration
ToolRegistry
BaseLLM.generate(tools=...)
```

Bu **Safety #8'in zorunlu bir güvenlik bug'ı değil**, ama #14'ün getirdiği yeni async execution boundary'sinin contract'ını tam oturtmayan bir architectural defect.

Ve bunu şimdi düzeltmek mantıklı. Çünkü ileride üçüncü bir tool execution modeli geldiğinde tekrar aynı refactoru yapmak istemiyoruz.

---

# 2. Policy engine fail-closed değil

Şu an:

```python
def _decide(self, risk_level):
    if LOW:
        return ALLOW
    elif MEDIUM:
        return ASK
    elif HIGH:
        return ASK
    elif CRITICAL:
        return DENY
```

Bugün dört `RiskLevel` var, dolayısıyla çalışıyor.

Ama Safety & Control açısından problem şu:

> Yarın `RiskLevel` enum'una yeni bir değer eklenirse ve burası unutulursa `_decide()` `None` döndürür.

Sonra `PolicyEvaluation.decision` beklenen `PolicyDecision` yerine `None` taşıyabilir.

Bu **fail-closed değil**.

Safety katmanında istediğimiz davranış:

```text
unknown/unhandled risk
        ↓
      DENY
```

Bu yüzden `_decide()` için explicit fail-closed default mantıklı.

Bu da speculative değil. Zaten #13'ün prensibi:

> yeni / bilinmeyen capability implicit allow almamalı.

Aynı prensibi policy decision boundary'sinde de korumak gerekiyor. Safe defaults testleri bugün `UNKNOWN` ve `UNTRUSTED` tool'ları doğrudan `DENY` yapıyor.

---

# 3. Workspace boundary tarafı: şu an temiz

Burada ekstra refactor önermiyorum.

`WorkspacePathGuard` root'u canonicalize ediyor ve her path'i `resolve()` sonrası `is_relative_to()` ile kontrol ediyor.

Testlerde:

* normal path
* `../` traversal
* absolute outside path
* symlink escape

var.

Bu kısma **dokunmayalım**.

---

# 4. Trust + policy + approval zinciri: mimari doğru

Şu anda akış:

```text
Tool Call
   ↓
ToolRegistry
   ↓
ToolRegistration
   ├── Tool
   └── TrustLevel
   ↓
PolicyContext
   ↓
PolicyEngine
   ↓
ALLOW / ASK / DENY
        │
        ├── ALLOW → execute
        │
        ├── ASK → ApprovalBroker → execute
        │
        └── DENY → failure result
```

Bu boundary güzel.

Özellikle `UNKNOWN` / `UNTRUSTED` doğrudan deny edilmesi iyi bir fail-closed davranış.

Burada yeni abstraction eklemiyorum.

---

# 5. Risk classifier: Safety #8 için yeterli

`DefaultRiskClassifier`:

* filesystem
* execution
* process control
* command execution
* privilege escalation
* destructive commands
* dependency mutation
* git operations
* sensitive targets

ayrımlarını yapıyor ve bilinmeyen durumlarda HIGH'a düşüyor.

Özellikle:

```text
missing command → HIGH
non-string command → HIGH
unparseable command → HIGH
unknown tool → HIGH
```

mantığı doğru.

Burada da **şimdilik yeni parser / shell AST / PowerShell parser falan yapmıyoruz.**

Bu zaten gelecekte ayrı bir security-hardening konusu olabilir; bugün #8'in sınırını gereksiz büyütmeyelim.

---

# 6. Auditability: yeterli, ama gelecekte genişleyecek

`AgentRuntime` şu event'leri emit ediyor:

```text
POLICY_EVALUATED
APPROVAL_REQUESTED
APPROVAL_COMPLETED
TOOL_INVOKED
TOOL_COMPLETED
TOOL_FAILED
```

ve audit emitter payload'ları redaction'dan geçiriyor.

Bu #8 için yeterli.

Ama ileride observability aşamasında:

* event correlation
* run ID
* iteration ID
* latency
* token usage
* persistent event stream

gibi şeyler gelecek.

**Şimdi bunlara dokunmayalım.**

---

# 7. Process safety: #14 ile gerçekten tamamlandı

Burada Sourcery'nin dört finding'inin tamamı resolved:

1. timeout fallback
2. cancellation error preservation
3. subprocess creation cancellation
4. kill-process cancellation cleanup

Sourcery bunların hepsini yeni `ProcessTerminator` / cancellation handling ile resolved olarak işaretlemiş.

`ProcessTerminator` artık ortak termination boundary'si.

Bu yüzden **#14'ü tekrar açıp process kodunu kurcalamak istemiyorum.**

---

# 8. CI / test durumu

Güncel merge commit `752382...` ve #22 merge edilmiş.

Senin son doğrulaman da:

```text
314 passed
```

CI tarafında Linux problemi de çözüldü ve ardından merge gerçekleşti.

Workflow şu anda sadece:

```text
pip install -e ".[dev]"
python -m pytest
```

çalıştırıyor.

`pyproject.toml` ise `slow` testleri default olarak dışarıda bırakıyor.

Bu şu an **Safety blocker değil**.

---

# Benim önerdiğim son kapanış planı

Şu anda Safety & Control'ı kapatmadan önce sadece **iki küçük, gerçek cleanup** yapalım:

### Cleanup 1 — Tool contract boundary

```text
SyncBaseTool
AsyncBaseTool
       ↓
    BaseTool
       ↓
ToolProvider
ToolRegistration
ToolRegistry
BaseLLM tool metadata
```

Burası #14 sonrası oluşan gerçek architectural inconsistency.

### Cleanup 2 — Policy fail-closed

Unhandled `RiskLevel` → `DENY`.

Bunun için bir regression test de ekleriz:

```text
unknown/unhandled risk
        ↓
       DENY
```

Sonra:

```text
314+ passed
CI green
```

ve **#8 Safety & Control gerçekten kapanabilir.**

---

## Ondan sonra ne olacak?

Bence asıl önemli nokta bu.

Safety & Control'dan sonra **hemen yeni feature spam'ine geçmemeliyiz.**

Şu an elimizde çok güzel bir temel var:

```text
AgentRuntime
   │
   ├── LLM
   ├── ToolRegistry
   │      ├── Sync tools
   │      └── Async tools
   │
   ├── PolicyEngine
   │      ├── Trust
   │      ├── Risk
   │      └── ALLOW / ASK / DENY
   │
   ├── ApprovalBroker
   │
   └── AuditEmitter
```

Bu noktada **#8 kapanışından sonra roadmap'i tekrar değerlendirmek** çok doğru olur.

Çünkü başlangıçta yazdığımız roadmap'in sonraki aşamaları artık mevcut gerçek mimariye göre yeniden sıralanabilir. Özellikle:

* Agent Runtime'ın ne kadarının gerçekten tamam olduğu
* Tool abstraction'ın async/sync düzeltmesinden sonra nasıl evrilmesi gerektiği
* Context Engineering'in ne zaman gerekli olduğu
* MCP'nin ne zaman girmesi gerektiği
* Execution'ın mevcut haliyle ne kadar production-ready olduğu

bunları **mevcut kod üzerinden** karar vermek daha doğru.

### Kısacası

**#8 için şu an “bitmiş” demiyorum.**

Önce:

1. **Tool contract typing cleanup**
2. **Policy fail-closed cleanup**
3. test + CI
4. sonra **#8'i kapat**

Bundan sonra da yeni issue açmadan önce mevcut mimariyi bir kez daha değerlendirip **bir sonraki milestone'un boundary'sini beraber belirleyelim.**

Bu, senin “bilinen boundary'yi şimdi doğru kur, geleceğin gereksiz sistemini şimdi kurma” prensibine tam oturuyor.
