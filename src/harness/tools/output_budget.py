

class OutputBudget:
    def __init__(self, max_chars: int):
        if max_chars <= 0:
            raise ValueError("max_chars must be greater than zero.")
        self.max_chars = max_chars


    def enforce(self, lines: list[str]) -> list[str]:
        if not lines:
            return []

        serialized_length = sum(len(line) for line in lines) + len(lines) - 1

        if serialized_length <= self.max_chars:
            return lines

        total_count = len(lines)
        candidate_lines = []
        candidate_length = 0

        for line in lines:
            separator_length = 0 if not candidate_lines else 1
            potential_length = candidate_length + separator_length + len(line)

            shown_count = len(candidate_lines) + 1
            notice = f"[truncated: {shown_count}/{total_count} lines - refine search]"

            if potential_length + 1 + len(notice) <= self.max_chars:
                candidate_lines.append(line)
                candidate_length = potential_length
            else:
                break

        if not candidate_lines:
            return []

        final_notice = (
            f"[truncated: {len(candidate_lines)}/{total_count} lines - refine search]"
        )

        return candidate_lines + [final_notice]