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