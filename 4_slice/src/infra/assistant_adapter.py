from src.domain.assistant import AssistantUnavailable


class FactOnlyAssistantAdapter:
    """Replace this adapter through configuration when using Ollama or an external LLM."""
    def answer(self, point, question):
        if not question.strip():
            raise ValueError("question must not be empty")
        return (f"O ponto {point.name} está com status {point.status.value}. "
                f"As linhas cadastradas são: {', '.join(point.lines) or 'nenhuma'}. "
                "Não possuo previsão de chegada.")


class UnavailableAssistantAdapter:
    def answer(self, point, question):
        raise AssistantUnavailable()
