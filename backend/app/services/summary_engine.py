import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

DISCLAIMER = "This is not a diagnosis — please consult your doctor"


def generate_summary(laboratory_tests: List[Dict[str, Any]],
                     abnormal_tests: List[Dict[str, Any]],
                     interpretations: List[Dict[str, Any]],
                     global_confidence: int) -> str:
    """
    Generate a patient-facing, plain-English summary of the lab report results.

    Args:
        laboratory_tests: List of all extracted lab tests
        abnormal_tests: List of abnormal lab tests
        interpretations: List of test interpretations from the knowledge engine
        global_confidence: Integer (0-100) representing overall extraction confidence

    Returns:
        A plain-English summary string ending with a disclaimer.
    """
    # 1. Fallback: No laboratory tests extracted
    if not laboratory_tests:
        return f"No laboratory tests were found or could be successfully extracted from the report. Please upload a clearer document or enter the values manually. {DISCLAIMER}."

    # 2. Fallback: Globally low confidence
    if global_confidence < 60:
        return f"We detected laboratory tests in the report, but the extraction confidence is low due to poor image or scan quality. Please review the extracted values carefully against your original report. {DISCLAIMER}."

    # 3. All normal results
    if not abnormal_tests:
        normal_names = [t["test_name"] for t in laboratory_tests if t.get("test_name")]
        normal_str = ", ".join(normal_names)
        
        overall_health_msg = "All of your extracted laboratory tests are within the normal reference ranges. No significant abnormalities were detected in the processed markers."
        
        return (
            f"Overall Health: {overall_health_msg}\n\n"
            f"Main Abnormal Findings: None.\n\n"
            f"Normal Findings: The following tests are normal: {normal_str}.\n\n"
            f"Lifestyle Advice: Continue maintaining a balanced lifestyle and staying physically active to support your health markers.\n\n"
            f"Doctor Consultation Advice: Continue regular check-ups with your healthcare provider as scheduled.\n\n"
            f"{DISCLAIMER}."
        )

    # 4. Abnormal findings present
    num_abnormal = len(abnormal_tests)
    findings = []
    for interp in interpretations:
        explanation = interp.get("explanation", "")
        if explanation:
            findings.append(explanation)

    if findings:
        findings_paragraph = ". ".join(findings) + "."
        overall_health_msg = f"Your report shows {num_abnormal} abnormal test result{'s' if num_abnormal > 1 else ''}. Specifically, {findings_paragraph}"
    else:
        overall_health_msg = f"Your report contains abnormal results. Please review the interpretation table below."

    # Traceable lists of tests
    normal_tests = [t for t in laboratory_tests if t not in abnormal_tests]
    normal_names = [t["test_name"] for t in normal_tests if t.get("test_name")]
    normal_str = ", ".join(normal_names) if normal_names else "None"

    abnormal_names_vals = []
    for t in abnormal_tests:
        name = t.get("test_name")
        val = t.get("value")
        unit = t.get("unit") or ""
        unit_str = f" {unit}" if unit else ""
        status = t.get("status", "abnormal")
        abnormal_names_vals.append(f"{name} ({val}{unit_str} is {status.lower()})")
    abnormal_str = ", ".join(abnormal_names_vals)

    # Generate Lifestyle Advice triggered only by the specific test types present (Anti-Hallucination)
    lifestyle_tips = []
    
    def has_test(pattern: str) -> bool:
        return any(pattern in t.get("test_name", "").lower() for t in laboratory_tests)

    if has_test("cholesterol") or has_test("lipid") or has_test("triglyceride") or has_test("ldl") or has_test("hdl"):
        lifestyle_tips.append("Consider a diet rich in soluble fiber and healthy unsaturated fats (like olive oil, nuts) while minimizing saturated fats to support healthy cholesterol levels.")
        
    if has_test("glucose") or has_test("sugar") or has_test("hba1c"):
        lifestyle_tips.append("Monitor carbohydrate and sugar intake, focus on whole grains, and engage in regular physical activity to help maintain stable blood glucose levels.")
        
    if has_test("hemoglobin") or has_test("rbc") or has_test("iron") or has_test("ferritin"):
        lifestyle_tips.append("Ensure dietary intake of iron-rich foods (such as dark leafy greens, beans, or lean meats) paired with Vitamin C to support hemoglobin and red blood cell production.")
        
    if has_test("vitamin d"):
        lifestyle_tips.append("Ensure safe sun exposure or include vitamin D-rich foods (like fortified dairy or fatty fish) in your meals.")
        
    if has_test("vitamin b12") or has_test("folate") or has_test("b12"):
        lifestyle_tips.append("Include sources of Vitamin B12 (such as eggs, dairy, or fortified foods) to support red blood cell and nerve health.")
        
    if has_test("creatinine") or has_test("urea") or has_test("kidney") or has_test("bun"):
        lifestyle_tips.append("Stay well-hydrated by drinking an adequate amount of water daily to support optimal kidney filtration.")

    lifestyle_str = " ".join(lifestyle_tips) if lifestyle_tips else "Maintain a general healthy, balanced diet and standard physical exercise."

    # Doctor advice: reference specific abnormal tests
    abn_list = ", ".join([t.get("test_name") for t in abnormal_tests])
    doctor_str = f"Please consult a doctor to discuss the abnormal results for {abn_list}."

    summary_text = (
        f"Overall Health: {overall_health_msg}\n\n"
        f"Main Abnormal Findings: {abnormal_str}.\n\n"
        f"Normal Findings: The following tests are normal: {normal_str}.\n\n"
        f"Lifestyle Advice: {lifestyle_str}\n\n"
        f"Doctor Consultation Advice: {doctor_str}\n\n"
        f"{DISCLAIMER}."
    )

    return summary_text
