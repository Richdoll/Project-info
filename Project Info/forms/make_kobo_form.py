"""Generates forms/kobo_evaluation_form.xlsx (XLSForm) to upload to KoboToolbox."""
from openpyxl import Workbook

LIK = "likert"
survey = []  # (type, name, label, required, relevant, constraint, appearance, calculation, read_only, constraint_message)

def q(type_, name, label, req=False, rel="", cons="", app="", calc="", ro="", msg=""):
    survey.append((type_, name, label, "yes" if req else "", rel, cons, app, calc, ro, msg))

def group(name, label): q("begin_group", name, label, app="")
def end(name): q("end_group", name, "")

group("s1", "SECTION 1: Evaluator information")
q("date", "evaluation_date", "Date of evaluation", True)
q("text", "name", "Your name (optional)")
q("select_one roles", "role", "Your role / profession", True)
q("text", "role_other", "Other profession", True, rel="${role}='other'")
q("select_one devices", "device", "How did you access the application?", True)
q("select_one yesno", "first_use", "Is this your first time using the application?", True)
q("select_one freq", "previous_uses", "How many times have you used it before?", rel="${first_use}='no'")
end("s1")

group("s2", "SECTION 2: First impression and interface")
for n, l in [("interface_attractive", "The interface is attractive and well designed"),
             ("easy_navigation", "The application is easy to navigate"),
             ("clear_menus", "Menus and buttons are clearly labelled"),
             ("fast_loading", "The application loads quickly"),
             ("works_on_device", "The application works well on my device")]:
    q(f"select_one {LIK}", n, l, True)
end("s2")

group("s3", "SECTION 3: Features and performance")
q("select_multiple features", "features_tested", "Which features did you test?", True)
for n, l in [("meets_needs", "The features meet my needs"),
             ("easy_to_use", "The features are easy to use"),
             ("accurate_results", "The results provided are accurate"),
             ("efficiency", "The application helps me complete my tasks efficiently"),
             ("clear_help", "The instructions and help are clear and useful")]:
    q(f"select_one {LIK}", n, l, True)
end("s3")

group("s4", "SECTION 4: Problems encountered")
q("select_one yesno", "problems", "Did you encounter any problems or errors?", True)
q("select_multiple problem_types", "problem_types_selected", "What type(s) of problem(s)?", rel="${problems}='yes'")
q("text", "problem_description", "Please describe the problem(s) in detail", rel="${problems}='yes'", app="multiline")
end("s4")

group("s5", "SECTION 5: Overall satisfaction")
q("integer", "rating", "Overall rating of the application", True, cons=". >= 0 and . <= 10", msg="The rating must be between 0 and 10.")
q("text", "satisfaction", "Satisfaction level", ro="yes",
  calc='if(${rating} >= 9, "Excellent", if(${rating} >= 7, "Very good", if(${rating} >= 5, "Good", if(${rating} >= 3, "Fair", "Poor"))))')
q("select_one recommend", "recommendation", "Would you recommend this application?", True)
q("select_one reuse", "reuse_intent", "Would you use this application again?", True)
end("s5")

group("s6", "SECTION 6: Suggestions for improvement")
q("text", "strengths", "What are the main strengths of this application?", True, app="multiline")
q("text", "improvements", "What could be improved?", True, app="multiline")
q("text", "missing_features", "Which missing features would you like to see added?", app="multiline")
q("text", "comments", "Additional comments or suggestions", app="multiline")
end("s6")
q("note", "thanks", "Thank you for your valuable feedback! Your comments will help us improve the application.")

choices = []
def ch(lst, items):
    for name, label in items:
        choices.append((lst, name, label))
ch("roles", [("student", "Student"), ("teacher", "Teacher"), ("researcher", "Researcher"),
             ("analyst", "Data analyst"), ("developer", "Developer"),
             ("project_manager", "Project manager"), ("other", "Other")])
ch("devices", [("computer", "Computer"), ("tablet", "Tablet"), ("smartphone", "Smartphone")])
ch("yesno", [("yes", "Yes"), ("no", "No")])
ch("freq", [("2_3", "2 to 3 times"), ("4_5", "4 to 5 times"), ("more_than_5", "More than 5 times")])
ch(LIK, [("1", "Strongly disagree"), ("2", "Disagree"), ("3", "Neutral"), ("4", "Agree"), ("5", "Strongly agree")])
ch("features", [("scraping", "Data collection (scraping)"), ("download", "Download"),
                ("form", "Form filling"), ("dashboard", "Data dashboard")])
ch("problem_types", [("loading", "Loading error"), ("display", "Display problem"),
                     ("not_working", "Feature not working"), ("data_loss", "Data loss"),
                     ("slow", "Slow performance"), ("confusing_interface", "Confusing interface"), ("other", "Other")])
ch("recommend", [("yes_definitely", "Yes, without hesitation"), ("yes_probably", "Yes, probably"),
                 ("maybe", "Maybe"), ("probably_not", "Probably not"), ("no", "No")])
ch("reuse", [("yes_regularly", "Yes, regularly"), ("yes_occasionally", "Yes, occasionally"),
             ("maybe", "Maybe"), ("probably_not", "Probably not"), ("no", "No")])

wb = Workbook()
s = wb.active; s.title = "survey"
s.append(["type", "name", "label", "required", "relevant", "constraint", "appearance", "calculation", "read_only", "constraint_message"])
for r in survey: s.append(list(r))
c = wb.create_sheet("choices"); c.append(["list_name", "name", "label"])
for r in choices: c.append(list(r))
st = wb.create_sheet("settings"); st.append(["form_title", "form_id"])
st.append(["Web application evaluation", "evaluation_app_web"])
wb.save("forms/kobo_evaluation_form.xlsx")
print("OK", len(survey), "survey rows,", len(choices), "choices")
