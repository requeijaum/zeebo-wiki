# Aprendido: max_tokens p/ lfm extração
- 800 tokens => `content` vazio (reasoning consome tudo). Medido F0 célula 1: 61s, 800/800, vazio.
- Uso: extração 2000, CoT 800→insuficiente, usar 1500+.
- Regra execução: se `content` vazio e `reasoning_tokens ≈ completion_tokens`, dobrar max_tokens.
