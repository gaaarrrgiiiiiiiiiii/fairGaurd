# FairGuard 3-Minute Hackathon Demo Script

## 0:00 - 0:30 | The Hook
**Speaker:** 
"Every company is rushing to deploy AI, but the EU AI Act just made biased AI illegal, with fines up to 35 million Euros. You can’t afford to let a biased algorithm deny a loan, reject a resume, or flag a patient. But auditing models takes weeks. 
What if you could intercept biased decisions *in real time*, right before they hit the user? 
**Meet FairGuard.** It’s essentially a firewall for your AI models."

## 0:30 - 1:30 | The Tech & Architecture
**Speaker:**
"Our startup operates as a sub-15 millisecond middleware. Developers drop our 5-line Python SDK over their existing XGBoost or LLM pipelines. 
*(Show architecture slide or code snippet)*
When a model makes a decision, FairGuard runs it through 4 distinct bias metrics in parallel and uses **DoWhy Causal Graphs** to prove if a protected attribute—like gender—caused the outcome. If the bias breaches our mathematical thresholds, our Counterfactual Engine intercepts and corrects the decision instantly.
Let me show you."

## 1:30 - 2:30 | Live Dashboard Demo
**Speaker:**
"Here is the FairGuard Live Dashboard monitoring our client's loan approval system."
*(Click the neon 'Run Demo Sequence' button)*
"Watch the real-time intercept feed. A male applicant with $55k income applies. The model approves him. FairGuard lets it pass. 
But look what happens next: Sarah, a female with the EXACT same financial profile applies. The biased model flags her as 'Denied'. 
Within milliseconds, FairGuard's firewall catches the demographic parity breach. The Causal graph lights up in yellow showing 'Sex' caused the denial. FairGuard explicitly intercepts the 'Denied' payload, computes a counterfactual fair probability, and forces an 'Approved' decision to the front-end, saving the company from a discrimination lawsuit."

## 2:30 - 3:00 | The Business Model / "The Ask"
**Speaker:**
"But compliance doesn’t stop at the intercept. 
*(Click 'Download Compliance Report' button)*
With one click, our system generates an instant, immutable EU AI Act Article 13 Post-Market Monitoring report for your legal team.
We are targeting enterprise FinTechs first and charging a SaaS API consumption model. 
FairGuard: Don't let your AI become your biggest liability."
*(End)*
