# API de Planejamento Curricular

Esta API permite planejar o currículo de um estudante baseado em disciplinas disponíveis, períodos preferidos e outras restrições.

## Instalação

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Execute a API:
```bash
python main.py
```

A API estará disponível em ``

## Endpoints

### POST /simulate

Planeja o currículo baseado nos parâmetros fornecidos.

#### Request Body:
```json
{
  "disciplines": [
    {
      "name": "Nome da Disciplina",
      "semester": 1,
      "attended": false,
      "workload": 60,
      "type": "OBG",
      "code": "DISC001",
      "timetables": [
        {
          "days": "SEG TER",
          "hours": "AB-M CD-M",
          "teacher": "Professor Nome"
        }
      ],
      "pre_requiriments": []
    }
  ],
  "preferred_periods": ["morning", "afternoon"],
  "max_workload": 600,
  "max_optative_workload": 400,
  "current_student_semester": 2,
  "ignore_tcc_period_filter": false
}
```

#### Parâmetros:
- `disciplines`: Array de disciplinas disponíveis
- `preferred_periods`: Períodos preferidos (morning, afternoon, evening)
- `max_workload`: Carga horária máxima por semestre
- `max_optative_workload`: Carga horária máxima de disciplinas optativas
- `current_student_semester`: Semestre atual do estudante
- `ignore_tcc_period_filter`: Se deve ignorar filtro de período para TCC

#### Response:
```json
{
  "quantity_semester": 8,
  "semesters": [...],
  "prediction_status": "success",
  "description": "matriz finalizada com sucesso!",
  "optative_workload_remaining": 100
}
```

### GET /

Endpoint raiz com informações sobre a API.

## Documentação da API

Acesse `/docs` para ver a documentação interativa da API (Swagger UI).

## Exemplo de Uso

```bash
curl -X POST "http://localhost:8000/plan-curriculum" \
     -H "Content-Type: application/json" \
     -d '{
       "disciplines": [...],
       "preferred_periods": ["morning", "afternoon"],
       "max_workload": 600,
       "max_optative_workload": 400,
       "current_student_semester": 2,
       "ignore_tcc_period_filter": false
     }'
``` 

# Planejador de Currículo com Inteligência Artificial

## Visão Geral

O `curriculum_planner_greedy_fixed.py` é um script Python que utiliza **inteligência artificial avançada** para criar um plano curricular acadêmico otimizado. Com um **algoritmo guloso guiado por uma heurística inteligente**, a IA aloca disciplinas obrigatórias (OBG) e optativas (OPT) de forma eficiente, respeitando restrições como pré-requisitos, conflitos de horário e limites de carga horária. A solução é rápida, considera disciplinas já cursadas e permite que a carga optativa ultrapasse 400 horas, garantindo um plano personalizado e eficaz.

## Objetivo

A IA foi projetada para simplificar o planejamento curricular, com os seguintes objetivos:
- Priorizar disciplinas obrigatórias (ex.: "ADM", "COMPILADORES", "TCC II").
- Evitar conflitos de horário e respeitar pré-requisitos.
- Adaptar-se a disciplinas optativas já cursadas, com flexibilidade na carga horária.
- Gerar um plano com o menor número de semestres possível.
- Fornecer logs detalhados para transparência e diagnóstico.

## Lógica do Algoritmo

### 1. Entrada
- **JSON**:
  - `name`: Nome da disciplina (ex.: "TCC II").
  - `code`: Identificador único (ex.: "04.505.49").
  - `semester`: Semestre sugerido (ex.: 8).
  - `attended`: Booleano indicando se já cursada.
  - `workload`: Carga horária (ex.: 80 horas).
  - `type`: "OBG" (obrigatória) ou "OPT" (optativa).
  - `timetables`: Lista de horários (dias, horas, professor).
  - `pre_requiriments`: Códigos de pré-requisitos.
- **Validação**: Modelos Pydantic (`Discipline`, `Timetable`) garantem consistência dos dados.

### 2. Filtragem Inteligente
- **Função `filter_valid_disciplines`**:
  - A IA filtra disciplinas com horários compatíveis com `preferred_periods=["morning", "afternoon", "evening"]`.
  - Para "TCC I/II", `ignore_tcc_period_filter=True` ignora restrições de período.
  - Disciplinas sem horários válidos (ex.: "LIBRAS") são registradas nos logs.

### 3. Verificação de Elegibilidade
- **Função `is_eligible`**:
  - A IA verifica se a disciplina não foi cursada e se todos os pré-requisitos estão atendidos.
  - Pré-requisitos faltantes são registrados para transparência.

### 4. Detecção de Conflitos
- **Função `has_conflict`**:
  - A IA identifica sobreposições de dias e horas entre horários.
  - Exemplo: "TER QUI CD-M" conflita com "TER CD-M", mas não com "TER AB-N".
  - Conflitos são registrados nos logs.

### 5. Heurística Inteligente
- **Função `calculate_discipline_score`**:
  - A IA atribui pontuações às disciplinas:
    - +100 para OBG, +50 para OPT, priorizando obrigatórias.
    - +20 por pré-requisito desbloqueado, acelerando o progresso.
    - Penalidade leve (-workload/10) para balancear a carga horária.
  - Essa heurística reflete a inteligência da IA em otimizar escolhas.

### 6. Algoritmo Guloso com IA
- **Função `plan_curriculum`**:
  - **Inicialização**:
    - Calcula a carga optativa inicial com base em disciplinas com `attended: true`.
    - Define `max_workload=800` (limite por semestre), `max_optative_workload=400` (meta flexível), e até 7 disciplinas por semestre.
  - **Loop por Semestre** (máximo 20):
    1. Filtra disciplinas elegíveis.
    2. Ordena por pontuação heurística.
    3. Aloca disciplinas, respeitando carga horária e horários.
    4. Atualiza carga optativa e disciplinas cursadas.
    5. Registra plano e carga acumulada nos logs.
  - **Parada**: Quando todas as OBG são alocadas, após 3 semestres vazios, ou se a carga optativa atinge/excede 400 horas (com optativas disponíveis).
  - **Flexibilidade**: Permite carga optativa acima de 400 horas.

### 7. Saída
- **Formato JSON**:
  - `quantity_semester`: Número de semestres.
  - `semesters`: Disciplinas alocadas por semestre (nome, código, horário, etc.).
  - `prediction_status`: "success" ou "error".
  - `description`: Ex.: "Matriz finalizada com sucesso usando IA!".
  - `disciplines_erros`: OBG não alocadas, com motivos.
  - `optative_workload_remaining`: Carga optativa restante.
- **Logs**: Mostram carga inicial, disciplinas filtradas, elegíveis, alocadas e conflitos.

### 8. Resumo
- **Heurística Avançada**: Simula raciocínio humano, priorizando OBG e desbloqueio de pré-requisitos.
- **Otimização Rápida**: Processa currículos complexos em segundos.
- **Adaptabilidade**: Ajusta-se a disciplinas cursadas e preferências de horário.
- **Transparência**: Logs detalhados mostram o processo decisório da IA.

## Como Usar

### Pré-requisitos
- Python 3.8+.
- Dependência:
  ```bash
  pip install -r requiriments.txt
  ```

### Entrada
- Crie `/content/disciplines.json`:
  ```json
  [
    {
      "name": "TCC II",
      "code": "04.505.49",
      "semester": 8,
      "attended": false,
      "workload": 40,
      "type": "OBG",
      "timetables": [{"days": "TER", "hours": "AB-N", "teacher": "FABIANA"}],
      "pre_requiriments": []
    },
    {
      "name": "OPTATIVA",
      "code": "04.505.XX",
      "semester": 1,
      "attended": true,
      "workload": 80,
      "type": "OPT",
      "timetables": [...],
      "pre_requiriments": []
    }
  ]
  ```

### Execução
1. Salve o código como `curriculum_planner_greedy_fixed.py`.
2. Coloque `disciplines.json` em `/content/`.
3. Execute:
   ```bash
   python curriculum_planner_greedy_fixed.py
   ```

### Exemplo de Saída
```json
{
  "quantity_semester": 2,
  "semesters": [
    [
      {
        "name": "TCC II",
        "code": "04.505.49",
        "timetable": {"days": "TER", "hours": "AB-N", "teacher": "FABIANA"},
        "workload": 40,
        "semester": 8,
        "type": "OBG"
      },
      ...
    ],
    ...
  ],
  "prediction_status": "success",
  "description": "Matriz finalizada com sucesso usando IA!",
  "optative_workload_remaining": 120
}
```

## Melhorias
- Backtracking para resolver conflitos.
- Priorização de optativas específicas.
- Interface gráfica com IA interativa.
