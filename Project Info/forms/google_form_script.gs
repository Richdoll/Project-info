/**
 * Creates the Google Form "Web application evaluation".
 * Usage: script.google.com > New project > paste this code > run createForm()
 * > authorize > read the links in View > Execution log.
 */
function createForm() {
  const form = FormApp.create("Web application evaluation");
  form.setDescription("Thank you for taking a few minutes to evaluate the application.");
  form.setProgressBar(true);
  form.setConfirmationMessage("Thank you for your valuable feedback! Your comments will help us improve the application.");

  const LIKERT = ["Strongly disagree", "Disagree", "Neutral", "Agree", "Strongly agree"];
  const likert = (t) => form.addMultipleChoiceItem().setTitle(t).setChoiceValues(LIKERT).setRequired(true);
  const single = (t, vals, req) => form.addMultipleChoiceItem().setTitle(t).setChoiceValues(vals).setRequired(req);
  const multi = (t, vals, req) => form.addCheckboxItem().setTitle(t).setChoiceValues(vals).setRequired(req);
  const para = (t, req) => form.addParagraphTextItem().setTitle(t).setRequired(req);

  // ---- SECTION 1 (page 1)
  form.addDateItem().setTitle("Date of evaluation").setRequired(true);
  form.addTextItem().setTitle("Your name (optional)");
  const ROLES = ["Student", "Teacher", "Researcher", "Data analyst", "Developer", "Project manager", "Other"];
  const role = single("Your role / profession", ROLES, true);

  const pOther = form.addPageBreakItem().setTitle("SECTION 1: Your profession");
  form.addTextItem().setTitle("Other profession").setRequired(true);

  const pAccess = form.addPageBreakItem().setTitle("SECTION 1: Evaluator information");
  single("How did you access the application?", ["Computer", "Tablet", "Smartphone"], true);
  const firstUse = single("Is this your first time using the application?", ["Yes", "No"], true);

  const pFreq = form.addPageBreakItem().setTitle("SECTION 1: Previous use");
  single("How many times have you used it before?", ["2 to 3 times", "4 to 5 times", "More than 5 times"], false);

  // ---- SECTION 2
  const pS2 = form.addPageBreakItem().setTitle("SECTION 2: First impression and interface");
  likert("The interface is attractive and well designed");
  likert("The application is easy to navigate");
  likert("Menus and buttons are clearly labelled");
  likert("The application loads quickly");
  likert("The application works well on my device");

  // ---- SECTION 3
  form.addPageBreakItem().setTitle("SECTION 3: Features and performance");
  multi("Which features did you test?",
        ["Data collection (scraping)", "Download", "Form filling", "Data dashboard"], true);
  likert("The features meet my needs");
  likert("The features are easy to use");
  likert("The results provided are accurate");
  likert("The application helps me complete my tasks efficiently");
  likert("The instructions and help are clear and useful");

  // ---- SECTION 4
  form.addPageBreakItem().setTitle("SECTION 4: Problems encountered");
  const problems = single("Did you encounter any problems or errors?", ["Yes", "No"], true);
  const pProblems = form.addPageBreakItem().setTitle("SECTION 4: Problem details");
  multi("What type(s) of problem(s)?",
        ["Loading error", "Display problem", "Feature not working", "Data loss",
         "Slow performance", "Confusing interface", "Other"], false);
  para("Please describe the problem(s) in detail", false);

  // ---- SECTION 5
  const pS5 = form.addPageBreakItem().setTitle("SECTION 5: Overall satisfaction");
  form.addScaleItem().setTitle("Overall rating of the application").setBounds(0, 10)
      .setLabels("0 = Very poor", "10 = Excellent").setRequired(true);
  // "Satisfaction level" (calculated field) does not exist in Google Forms: see the Kobo form.
  single("Would you recommend this application?",
         ["Yes, without hesitation", "Yes, probably", "Maybe", "Probably not", "No"], true);
  single("Would you use this application again?",
         ["Yes, regularly", "Yes, occasionally", "Maybe", "Probably not", "No"], true);

  // ---- SECTION 6
  form.addPageBreakItem().setTitle("SECTION 6: Suggestions for improvement");
  para("What are the main strengths of this application?", true);
  para("What could be improved?", true);
  para("Which missing features would you like to see added?", false);
  para("Additional comments or suggestions", false);

  // ---- CONDITIONAL LOGIC (page navigation)
  role.setChoices(ROLES.map(r => role.createChoice(r, r === "Other" ? pOther : pAccess)));
  firstUse.setChoices([firstUse.createChoice("Yes", pS2), firstUse.createChoice("No", pFreq)]);
  problems.setChoices([problems.createChoice("Yes", pProblems), problems.createChoice("No", pS5)]);

  Logger.log("Link to share: " + form.getPublishedUrl());
  Logger.log("Edit link: " + form.getEditUrl());
}
