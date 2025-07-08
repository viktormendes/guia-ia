from pydantic import BaseModel
from typing import List
import json
import copy
import random

# Modelos Pydantic para validação
class Timetable(BaseModel):
    days: str
    hours: str
    teacher: str

class Discipline(BaseModel):
    name: str
    semester: int
    attended: bool
    workload: int
    type: str
    code: str
    timetables: List[Timetable]
    pre_requiriments: List[str]

# Map timetable codes to time periods
period_map = {
    "AB-M": "morning", "CD-M": "morning",
    "AB-T": "afternoon", "CD-T": "afternoon",
    "AB-N": "evening", "CD-N": "evening"
}

# Check if a timetable is in the preferred period
def is_period_allowed(timetable, periods, discipline_name, ignore_tcc_period_filter):
    tcc_names = ["TCC 1", "TCC 2", "TCC I", "TCC II"]
    if ignore_tcc_period_filter and any(tcc_name in discipline_name for tcc_name in tcc_names):
        return True
    first_hour = timetable["hours"].split()[0] if timetable["hours"] else ""
    period = period_map.get(first_hour, "")
    return period in periods

# Check for time conflicts between two timetables
def has_conflict(timetable1, timetable2):
    days1, hours1 = timetable1["days"].split(), timetable1["hours"].split()
    days2, hours2 = timetable2["days"].split(), timetable2["hours"].split()
    for i in range(len(days1)):
        for j in range(len(days2)):
            if days1[i] == days2[j] and hours1[i] == hours2[j]:
                return True
    return False

# Check if a discipline's prerequisites are met
def is_eligible(discipline, attended_codes):
    if discipline["attended"]:
        return False
    missing_prereqs = [prereq for prereq in discipline["pre_requiriments"] if prereq not in attended_codes]
    if missing_prereqs:
        print(f"Disciplina {discipline['name']} ({discipline['code']}) não elegível: faltam pré-requisitos {missing_prereqs}")
        return False
    return True

# Filter disciplines with valid timetables
def filter_valid_disciplines(disciplines, preferred_periods, ignore_tcc_period_filter):
    valid_disciplines = []
    for d in disciplines:
        valid_timetables = [t for t in d["timetables"] if is_period_allowed(t, preferred_periods, d["name"], ignore_tcc_period_filter)]
        if valid_timetables:
            d_copy = copy.deepcopy(d)
            d_copy["timetables"] = valid_timetables
            valid_disciplines.append(d_copy)
        else:
            print(f"Disciplina {d['name']} ({d['code']}) filtrada: sem horários compatíveis")
    return valid_disciplines

# Heuristic score for a discipline
def calculate_discipline_score(discipline, valid_disciplines, attended_codes):
    score = 0
    if discipline["type"] == "OBG":
        score += 100  # Priorize OBG
    else:
        score += 50   # Menor prioridade para OPT
    # Bonus for unlocking prerequisites
    unlocks = sum(1 for d in valid_disciplines if discipline["code"] in d["pre_requiriments"] and not d["attended"])
    score += unlocks * 20
    # Penalize high workload to avoid exceeding max_workload
    score -= discipline["workload"] // 10
    return score

# Greedy curriculum planner
def plan_curriculum(disciplines, preferred_periods=["morning", "afternoon", "evening"], max_workload=800, max_optative_workload=400, current_student_semester=2, ignore_tcc_period_filter=True):
    valid_disciplines = filter_valid_disciplines(disciplines, preferred_periods, ignore_tcc_period_filter)
    attended_codes = set(d["code"] for d in valid_disciplines if d["attended"])
    current_optative_workload = sum(d["workload"] for d in valid_disciplines if d["attended"] and d["type"] == "OPT")
    print(f"Carga optativa inicial: {current_optative_workload} horas (disciplinas cursadas: {[d['name'] for d in valid_disciplines if d['attended'] and d['type'] == 'OPT']})")
    
    max_semesters = 20
    max_disciplines_per_semester = 7

    plan = []
    current_semester = current_student_semester
    empty_semesters = 0

    while any(not d["attended"] for d in valid_disciplines if d["type"] == "OBG") or (current_optative_workload < max_optative_workload and any(not d["attended"] for d in valid_disciplines if d["type"] == "OPT")):
        if current_semester > max_semesters:
            print(f"Semestre {current_semester}: Limite de semestres atingido")
            break

        eligible_disciplines = [d for d in valid_disciplines if is_eligible(d, attended_codes)]
        if not eligible_disciplines:
            print(f"Semestre {current_semester}: Nenhuma disciplina elegível restante")
            break

        print(f"Semestre {current_semester}: Disciplinas elegíveis: {[d['name'] for d in eligible_disciplines]}")
        # Sort disciplines by heuristic score
        eligible_disciplines.sort(key=lambda d: calculate_discipline_score(d, valid_disciplines, attended_codes), reverse=True)

        semester_plan = []
        current_workload = 0
        occupied_slots = []

        for discipline in eligible_disciplines:
            if len(semester_plan) >= max_disciplines_per_semester:
                break
            for timetable in discipline["timetables"]:
                if current_workload + discipline["workload"] > max_workload:
                    print(f"Semestre {current_semester}: Disciplina {discipline['name']} ({discipline['code']}) excede carga horária ({current_workload + discipline['workload']} > {max_workload})")
                    break
                conflict = False
                for t in occupied_slots:
                    if has_conflict(timetable, t):
                        conflict = True
                        print(f"Semestre {current_semester}: Conflito de horário para {discipline['name']} ({discipline['code']}) com {t}")
                        break
                if not conflict:
                    semester_plan.append({
                        "name": discipline["name"],
                        "code": discipline["code"],
                        "timetable": timetable,
                        "workload": discipline["workload"],
                        "semester": discipline["semester"],
                        "type": discipline["type"]
                    })
                    discipline["attended"] = True
                    attended_codes.add(discipline["code"])
                    current_workload += discipline["workload"]
                    if discipline["type"] == "OPT":
                        current_optative_workload += discipline["workload"]
                    occupied_slots.append(timetable)
                    break

        if not semester_plan:
            empty_semesters += 1
            print(f"Semestre {current_semester}: Nenhum plano gerado (semestre vazio)")
            if empty_semesters >= 3:
                break
        else:
            empty_semesters = 0
            plan.append(semester_plan)
            print(f"Semestre {current_semester}: Plano gerado com {len(semester_plan)} disciplinas: {[d['name'] for d in semester_plan]}")
            print(f"Semestre {current_semester}: Carga optativa acumulada: {current_optative_workload} horas")

        current_semester += 1

    # Construct final response
    result = {
        "quantity_semester": len(plan),
        "semesters": plan,
    }

    disciplines_errors = []
    alocated_codes = set(d["code"] for d in disciplines if d["attended"])
    for semester in plan:
        for course in semester:
            alocated_codes.add(course["code"])

    for d in disciplines:
        if d["code"] in alocated_codes:
            continue
        if d["type"] == "OPT":
            continue
        reason = []
        if any(prereq not in attended_codes for prereq in d["pre_requiriments"]):
            reason.append("pré-requisitos não atendidos")
        if not any(is_period_allowed(t, preferred_periods, d["name"], ignore_tcc_period_filter) for t in d["timetables"]):
            reason.append("sem horários disponíveis no período permitido")
        if not reason:
            reason.append("conflito de horário ou limite de carga horária")
        disciplines_errors.append({
            "name": d["name"],
            "code": d["code"],
            "type": d["type"],
            "reason": ", ".join(reason)
        })

    optative_remaining = max(0, max_optative_workload - current_optative_workload)

    if disciplines_errors:
        result["prediction_status"] = "error"
        result["description"] = "Algumas disciplinas foram impossíveis de alocar"
        result["disciplines_erros"] = disciplines_errors
    else:
        result["prediction_status"] = "success"
        result["description"] = "Matriz finalizada com sucesso usando algoritmo guloso com heurística!"

    result["optative_workload_remaining"] = optative_remaining

    return result

# Função para carregar e executar o planejamento
def main():
    try:
        with open("/content/disciplines.json", "r") as file:
            disciplines_data = json.load(file)
        
        disciplines = [Discipline(**d).model_dump() for d in disciplines_data]
        
        params = {
            "disciplines": disciplines,
            "preferred_periods": ["morning", "afternoon", "evening"],
            "max_workload": 800,
            "max_optative_workload": 400,
            "current_student_semester": 2,
            "ignore_tcc_period_filter": True
        }
        
        result = plan_curriculum(**params)
        
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    except FileNotFoundError:
        print("Erro: Arquivo /content/disciplines.json não encontrado.")
    except Exception as e:
        print(f"Erro: {str(e)}")

if __name__ == "__main__":
    main()
