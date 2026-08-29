# KUTLANG — Supervisor Status & Development Direction

> Türkçe durum raporu. Bu dosya, projeyi yöneten coding-agent harness / OpenCode gibi bir supervisor'ın mevcut durumu, alınan kararlar ve sıradaki hedefleri hızlıca anlayabilmesi için tutulur.

## Güncel Durum — 29 Ağustos 2026

KUTLANG, **Foundation & Agent Core** aşamasını tamamladı.

Mevcut sistemin en doğru tanımı:

> **Model-agnostic, tool-capable, tested single-agent coding runtime foundation.**

### Son doğrulama

- Full test suite: **161 passed**.
- CI: **green**.
- Son geliştirme branch'i başarıyla merge edildi.
- Merge sonrasında branch silindi.
- Slow test'ler local olarak çalışıyor; ancak CI'daki `python -m pytest -m slow` adımı environment tarafından cancel edildiği için required CI gate olmaktan çıkarıldı. Slow test'ler gerektiğinde manuel/ayrı validation olarak çalıştırılabilir.

## Şu Ana Kadar İnşa Edilen Temel

- Domain contract'ları ve typed modeller.
- `Message`, `ToolCall`, `ToolResult` gibi runtime modelleri.
- `AgentRuntime` ile LLM/provider katmanının ayrılması.
- `BaseLLM` / provider abstraction.
- Tool abstraction.
- Tool registry ve discovery.
- Request/response validation.
- Shell/process execution foundation.
- Configuration ve dependency injection.
- Multi-tool-call protocol correctness.
- Unit/integration test coverage ve CI.

Özellikle runtime'ın belirli bir modele veya provider'a gömülmemesi artık ana mimari invariant'lardan biridir.

## Mimari Felsefe

KUTLANG **mevcut coding-agent dünyasını from scratch yeniden yazma projesi değildir**.

Olgun bir open-source implementation, protocol, library, model server, language server, MCP implementation veya agent component problemi iyi çözüyorsa onu kullanmak tercih edilir. KUTLANG'ın sahip olduğu değer; domain sınırları, runtime orchestration, safety/policy, context strategy, evidence, reproducibility ve entegrasyon semantiğidir.

Hedef:

```text
Understand
    ↓
Gather Context
    ↓
Plan
    ↓
Act
    ↓
Observe
    ↓
Verify
    ↓
Iterate
```

## Sıradaki Büyük Aşama: Safety & Control

İlk sonraki issue:

**KUT-6 — Introduce workspace-scoped permission evaluation and approval flow**

Öncelik sırası:

1. Workspace boundary ve canonical path validation.
2. Symlink/path traversal protection.
3. Tool + arguments + execution context üzerinden risk classification.
4. `ALLOW / ASK / DENY` policy engine.
5. Transport-independent approval broker.
6. Command policy ve destructive command handling.
7. Cancellation, timeout ve process cleanup hardening.
8. Audit events + secret redaction.
9. New/external tool'lar için safe default.

Temel akış:

```text
ToolExecutionRequest
        ↓
RiskClassifier
        ↓
PolicyEngine
   ↙    ↓    ↘
ALLOW  ASK   DENY
        ↓
ApprovalBroker
        ↓
Tool Execution
```

Policy, tool implementation'larından bağımsız olmalıdır. LLM'nin “call et” demesi tek başına execution yetkisi değildir.

## Sonraki Aşamalar

### 2 — Transactional Workspace / Rollback

Agent değişiklikleri güvenli ve geri alınabilir olmalı.

- Before/after file hashes.
- Diff/patch artifacts.
- Transaction log.
- Checkpoints.
- Rollback.
- Kullanıcının önceden var olan dirty changes'lerini koruma.
- Gerekirse isolated git worktree/branch.

Hedef execution discipline:

```text
Inspect → Plan → Approval → Patch → Format → Test → Diff Review → Evidence
```

### 3 — Context Engineering & Coding Intelligence

- Git-aware repository inventory.
- Lexical search.
- `AGENTS.md` / project instructions hierarchy.
- Context prioritization.
- Token budget.
- Tool-output truncation.
- Automatic compaction.
- AST/symbol/repository map.
- LSP provider.

### LSP Açılımı

Buradaki LSP **Language Server Protocol** demektir; Liskov Substitution Principle değildir.

LSP üzerinden hedeflenen kabiliyetler:

- diagnostics
- go-to-definition
- find references
- hover
- document symbols
- workspace symbols
- rename

### 4 — Sessions & Runtime UX

- SQLite session persistence.
- Session / turn / tool invocation / artifact modelleri.
- SSE runtime event stream.
- Transactional changes.
- Checkpoints/rollback.
- `Plan / Build / Review / Verify` profiles.
- Resume/retry/undo/replay.

### 5 — Extensibility & Evaluation

- First-class MCP provider.
- Local stdio MCP first.
- Server lifecycle/health/reconnect.
- Namespaced tools.
- Per-server permission profile.
- Capability-aware model adapters.
- Provider routing/retry/fallback.
- Explicit project skills/instructions.
- Provider-independent evaluation harness.
- Deterministic regression tasks.
- Trace replay.
- Observability/failure taxonomy.

### 6 — Developer Surfaces

- CLI/TUI first.
- VS Code.
- Web/API.
- Remote execution.
- Multi-session/team/workspace.

### Future — Self-Evolution

Self-evolution, autonomous strategy adaptation ve multi-agent sistemleri ancak safety + replay + eval + regression protection olgunlaştıktan sonra ele alınacak.

## Native Tool Calling vs Prompt Fallback

### Native tool calling

Provider/API, tool'ları first-class structured protocol olarak destekler. Request içinde tool schema gönderilir ve response içinde structured `tool_calls` alınır.

### Prompt-parse fallback

Native tool calling yoksa modelden strict textual/JSON bir tool-call formatı üretmesi istenir. KUTLANG bunu parse edip aynı `ToolCall` domain modeline normalize eder.

Her iki yol da aynı güvenlik sınırına girmelidir:

```text
Provider response
      ↓
+-----+----------------+
| Native adapter      |
| Prompt-parse adapter|
+----------+----------+
           ↓
     Unified ToolCall
           ↓
   Schema validation
           ↓
    Policy / Approval
           ↓
       Execution
```

Parser hiçbir koşulda doğrudan tool çalıştırmamalıdır.

Önerilen configuration davranışı:

```text
tool_call_strategy: auto
# auto | native_only | prompt_fallback_only
```

## Evals Ne Demek?

Buradaki “evals”, genel anlamda **agent evaluation infrastructure** demektir; OpenAI'nin `openai/evals` framework'üne bağımlılık anlamına gelmez.

İlk eval sistemi provider-independent ve local-first olmalı.

Örnek task:

```text
“Bu fonksiyondaki off-by-one hatasını düzelt, testleri geçir.”
```

Grader mümkün olduğunca deterministik olmalı:

- task success
- tests passed
- changed files
- policy violations
- tool calls
- iteration count
- latency
- token/cost
- rollback behavior

LLM-as-a-judge daha sonra plan kalitesi veya evidence completeness gibi semantik özelliklerde kullanılabilir; security/correctness için tek otorite olmamalıdır.

## Local-Only / Offline Hedefi

KUTLANG local-first çalışabilmeli ve açıkça tanımlanmış bir `local-only` profile sahip olmalıdır.

```text
KUTLANG
   ↓
Local provider
   ↓
llama.cpp / Ollama / localhost-compatible server
   ↓
Local model weights
   ↓
Local filesystem + process + Git + LSP
```

Offline çalışmanın koşulları:

- Model weights local.
- Inference server local.
- Repo local.
- Tools local.
- LSP local.
- Gereken MCP server'ları local stdio.
- Network egress default-deny.

`git push`, remote MCP, browser/network tools, package downloads, cloud providers ve telemetry local-only profilde kapalı/deny olmalıdır.

**%100 offline garantisi**, network-isolated integration test yapılmadan iddia edilmemelidir.

## External Architecture Review — Perplexity

Perplexity ile yapılan bağımsız mimari değerlendirme KUTLANG'ın mevcut seviyesini şu şekilde tanımladı:

> **“Model-agnostic, tool-capable, tested single-agent coding runtime foundation.”**

Özellikle güçlü bulunan noktalar:

- AgentRuntime → BaseLLM ayrımı.
- Tool registry/discovery.
- Process manager yaklaşımı.
- Typed `Message`, `ToolCall`, `ToolResult` modelleri.
- Dependency override ile test isolation.
- DI ile configuration/import-time sorunlarının çözülmesi.
- Multi-tool-call protocol correctness.

Önerilen öncelik sırası:

1. Safety & Control.
2. Transactional workspace / rollback.
3. Context engineering.
4. Language Server Protocol.
5. Plan / Build / Review / Verify.
6. Session persistence.
7. Streaming event protocol.
8. Model capabilities/routing.
9. MCP / skills / plugin surfaces.
10. Evaluation / deterministic replay / observability.
11. Self-evolution ve multi-agent daha sonra.

### Review'dan Benimsenen İlkeler

- PolicyEngine tool implementation'ından bağımsız.
- Risk yalnız tool adına değil, tool + args + context'e göre.
- Yeni/external tool default olarak `ASK` veya `DENY`.
- Workspace mutation transaction/rollback destekli.
- Context bütçeli ve relevance-aware.
- Lexical search + AST/symbol index, gereksiz vector DB'den önce.
- LSP provider boundary arkasında.
- Runtime event'leri transport-independent.
- Native ve prompt-parsed tool calls tek domain modeline normalize.
- Safety/correctness eval'leri deterministik.
- Local-only explicit policy profile.
- Evidence-driven completion temel ürün özelliği.

### Şimdilik Yapılmayacaklar

- Mature agent framework'lerini from scratch yeniden yazmak.
- Gereksiz onlarca LLM provider.
- Custom vector database.
- Eval olmadan autonomous self-improvement.
- Single-agent reliability oturmadan multi-agent swarm.
- Messaging platform gateway'leri.
- Erken ağır web/Electron UI.
- Devasa MCP catalog.

## Supervisor'a Kısa Talimat

KUTLANG şu anda foundation aşamasını geçmiş durumdadır. Yeni geliştirmelerde önce **Safety & Control** tamamlanmalıdır. Yeni feature önerirken aşağıdaki sıralamayı koru:

```text
Safety
  ↓
Rollback / Transactions
  ↓
Context + LSP
  ↓
Sessions + Events
  ↓
MCP + Capabilities + Skills
  ↓
Evals + Replay + Observability
  ↓
CLI / VS Code / Web / API
  ↓
Self-Evolution / Multi-Agent
```

Her yeni abstraction için önce gerçek bir problem ve en az bir somut implementation ihtiyacı ara. Mevcut mature ecosystem çözümü varsa yeniden yazmak yerine entegre et.

Her agent completion'ı mümkün olduğunca **evidence-driven** yap: ne değişti, hangi komutlar çalıştı, hangi testler geçti, hangi policy kararları verildi ve neyin doğrulanmadığı açıkça görülebilsin.
