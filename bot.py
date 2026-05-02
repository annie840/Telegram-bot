import logging
import math
import random
import os
from datetime import datetime, time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# ── CONFIG ────────────────────────────────────────────────────────────────────
TOKEN = os.environ.get("BOT_TOKEN")
WEBSITE_URL = "https://sites.google.com/creativealignmentz.com/creative-alignmentz/home"
CALENDAR_URL = "https://calendar.app.google/1FfNk5Q2hfZLeN7N6"
TEACHER_CHAT_ID = None  # ← Set to your numeric Telegram chat ID to receive forwarded messages

# ── LOGGING ───────────────────────────────────────────────────────────────────
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ── SUBSCRIBER STORAGE (in-memory; replace with a DB for production) ──────────
# { chat_id: { "name": str, "subscribed": bool, "awaiting_message": bool } }
subscribers = {}

# ── 700 VOCABULARY WORDS ──────────────────────────────────────────────────────
words = [
    {"word": "Ability", "definition": "The power or skill to do something", "example": "She has the ability to speak three languages."},
    {"word": "Absence", "definition": "The state of being away from a place", "example": "His absence from class was noticed."},
    {"word": "Accurate", "definition": "Free from errors; correct", "example": "The report was accurate and detailed."},
    {"word": "Achievement", "definition": "A thing done successfully with effort", "example": "Winning the award was a great achievement."},
    {"word": "Acquire", "definition": "To get or obtain something", "example": "She wanted to acquire new skills."},
    {"word": "Adapt", "definition": "To adjust to new conditions", "example": "Animals adapt to their environment."},
    {"word": "Adequate", "definition": "Enough; satisfactory", "example": "The food supply was adequate for everyone."},
    {"word": "Admire", "definition": "To regard with respect or warm approval", "example": "I admire her patience and kindness."},
    {"word": "Advance", "definition": "To move forward or make progress", "example": "Technology continues to advance rapidly."},
    {"word": "Advice", "definition": "Guidance or recommendations offered", "example": "He gave me good advice about my career."},
    {"word": "Afford", "definition": "To have enough money to pay for something", "example": "Can you afford a new car?"},
    {"word": "Afraid", "definition": "Feeling fear or anxiety", "example": "She was afraid of the dark."},
    {"word": "Agree", "definition": "To have the same opinion", "example": "We both agree on the plan."},
    {"word": "Alert", "definition": "Quick to notice and respond", "example": "Stay alert while driving."},
    {"word": "Allow", "definition": "To give permission for something", "example": "They allow pets in this building."},
    {"word": "Ambition", "definition": "A strong desire to achieve something", "example": "Her ambition drove her to succeed."},
    {"word": "Ancient", "definition": "Very old; from long ago", "example": "They visited an ancient temple."},
    {"word": "Announce", "definition": "To make a public statement about something", "example": "The company will announce the results tomorrow."},
    {"word": "Answer", "definition": "A response to a question", "example": "Please give a clear answer."},
    {"word": "Anxious", "definition": "Worried or nervous", "example": "He felt anxious before the exam."},
    {"word": "Approach", "definition": "A way of dealing with something", "example": "We need a new approach to the problem."},
    {"word": "Argue", "definition": "To give reasons for or against something", "example": "They always argue about money."},
    {"word": "Arrange", "definition": "To put in order or make plans", "example": "She arranged the flowers beautifully."},
    {"word": "Assist", "definition": "To help someone do something", "example": "Can you assist me with this task?"},
    {"word": "Assume", "definition": "To think something is true without proof", "example": "Don't assume he is wrong."},
    {"word": "Attempt", "definition": "An effort to achieve something", "example": "This is her third attempt at the test."},
    {"word": "Attend", "definition": "To be present at an event", "example": "Will you attend the meeting?"},
    {"word": "Attract", "definition": "To cause interest or liking", "example": "The display attracted many visitors."},
    {"word": "Avoid", "definition": "To keep away from something", "example": "Try to avoid eating too much sugar."},
    {"word": "Aware", "definition": "Having knowledge of something", "example": "Are you aware of the rules?"},
    {"word": "Balance", "definition": "A state of equal weight or amount", "example": "Keep a balance between work and rest."},
    {"word": "Barrier", "definition": "Something that blocks progress", "example": "Language can be a barrier to communication."},
    {"word": "Behave", "definition": "To act in a certain way", "example": "Children should behave well in school."},
    {"word": "Belief", "definition": "Something accepted as true", "example": "It is my belief that honesty is important."},
    {"word": "Belong", "definition": "To be a member of a group", "example": "I belong to a reading club."},
    {"word": "Benefit", "definition": "An advantage or profit", "example": "Exercise has many health benefits."},
    {"word": "Blame", "definition": "To hold responsible for a fault", "example": "Don't blame others for your mistakes."},
    {"word": "Bold", "definition": "Confident and brave", "example": "She made a bold decision."},
    {"word": "Borrow", "definition": "To take something with intent to return it", "example": "Can I borrow your pen?"},
    {"word": "Brief", "definition": "Short in duration or length", "example": "Please give a brief summary."},
    {"word": "Broad", "definition": "Wide; covering many things", "example": "She has a broad knowledge of history."},
    {"word": "Budget", "definition": "A plan for spending money", "example": "Stick to your monthly budget."},
    {"word": "Build", "definition": "To construct something", "example": "They will build a new school."},
    {"word": "Burden", "definition": "A heavy load or responsibility", "example": "Debt can be a huge burden."},
    {"word": "Calculate", "definition": "To determine by mathematics", "example": "Calculate the total cost carefully."},
    {"word": "Capable", "definition": "Having the ability to do something", "example": "She is capable of great things."},
    {"word": "Career", "definition": "A person's working life", "example": "She has had a successful career in medicine."},
    {"word": "Careful", "definition": "Taking caution to avoid harm", "example": "Be careful when crossing the road."},
    {"word": "Cause", "definition": "Something that makes something happen", "example": "What was the cause of the accident?"},
    {"word": "Certain", "definition": "Known for sure; confident", "example": "I am certain he will come."},
    {"word": "Challenge", "definition": "A difficult task or problem", "example": "Learning a language is a great challenge."},
    {"word": "Change", "definition": "To become different", "example": "The weather can change quickly."},
    {"word": "Character", "definition": "The qualities that make someone unique", "example": "Honesty is part of his character."},
    {"word": "Choice", "definition": "An act of selecting something", "example": "Make the right choice."},
    {"word": "Citizen", "definition": "A member of a country or city", "example": "Every citizen has rights and duties."},
    {"word": "Claim", "definition": "To state something as a fact", "example": "She claims she saw the accident."},
    {"word": "Clear", "definition": "Easy to understand; transparent", "example": "Please make your instructions clear."},
    {"word": "Clever", "definition": "Quick to learn and understand", "example": "He gave a clever answer."},
    {"word": "Collect", "definition": "To gather things together", "example": "She likes to collect stamps."},
    {"word": "Combine", "definition": "To join two or more things together", "example": "Combine flour and water to make dough."},
    {"word": "Commit", "definition": "To dedicate oneself to something", "example": "Commit to your goals every day."},
    {"word": "Common", "definition": "Occurring frequently; widespread", "example": "Colds are very common in winter."},
    {"word": "Compare", "definition": "To examine similarities and differences", "example": "Compare the two prices before buying."},
    {"word": "Complete", "definition": "Having all parts; finished", "example": "The work is complete."},
    {"word": "Complex", "definition": "Made of many connected parts", "example": "This is a complex problem."},
    {"word": "Concern", "definition": "A feeling of worry; to be about", "example": "Her health is my main concern."},
    {"word": "Confident", "definition": "Feeling sure about oneself", "example": "She felt confident during the presentation."},
    {"word": "Connect", "definition": "To link or join things together", "example": "Connect the cables to the device."},
    {"word": "Consider", "definition": "To think carefully about", "example": "Consider all your options before deciding."},
    {"word": "Content", "definition": "Satisfied; material contained within", "example": "She was content with her results."},
    {"word": "Continue", "definition": "To keep doing something", "example": "Continue reading after the break."},
    {"word": "Control", "definition": "Power to manage or direct", "example": "She kept control of the situation."},
    {"word": "Convince", "definition": "To persuade someone to believe something", "example": "He tried to convince her to stay."},
    {"word": "Correct", "definition": "Free from error; right", "example": "That is the correct answer."},
    {"word": "Create", "definition": "To bring something into existence", "example": "Artists create beautiful works."},
    {"word": "Culture", "definition": "The beliefs and practices of a group", "example": "I enjoy learning about different cultures."},
    {"word": "Curious", "definition": "Eager to know or learn something", "example": "Children are naturally curious."},
    {"word": "Damage", "definition": "Physical harm that reduces value", "example": "The storm caused serious damage."},
    {"word": "Debate", "definition": "A formal discussion of opposing views", "example": "There was a debate about the new policy."},
    {"word": "Decide", "definition": "To make a choice", "example": "She decided to study abroad."},
    {"word": "Define", "definition": "To explain the meaning of something", "example": "Can you define this word for me?"},
    {"word": "Delay", "definition": "To make something happen later", "example": "Traffic caused a delay."},
    {"word": "Deliver", "definition": "To bring something to a place", "example": "The package will be delivered tomorrow."},
    {"word": "Demand", "definition": "An urgent request; to ask firmly", "example": "There is a high demand for nurses."},
    {"word": "Deny", "definition": "To say something is not true", "example": "He denied any involvement."},
    {"word": "Describe", "definition": "To say what something is like", "example": "Describe the place where you grew up."},
    {"word": "Desire", "definition": "A strong wish for something", "example": "She has a strong desire to travel."},
    {"word": "Develop", "definition": "To grow or improve over time", "example": "Develop good study habits early."},
    {"word": "Difference", "definition": "A way in which things are not the same", "example": "There is a big difference between the two."},
    {"word": "Difficult", "definition": "Not easy; requiring effort", "example": "The exam was very difficult."},
    {"word": "Direct", "definition": "Straight; without detours", "example": "Take the direct route to save time."},
    {"word": "Discover", "definition": "To find something for the first time", "example": "Scientists discover new species every year."},
    {"word": "Discuss", "definition": "To talk about something in detail", "example": "Let's discuss the project plan."},
    {"word": "Distance", "definition": "The space between two points", "example": "What is the distance to the city?"},
    {"word": "Doubt", "definition": "A feeling of uncertainty", "example": "I have no doubt she will succeed."},
    {"word": "Dream", "definition": "A hope or ambition; images during sleep", "example": "Follow your dreams."},
    {"word": "Drive", "definition": "To operate a vehicle; to motivate", "example": "What drives you to succeed?"},
    {"word": "Due", "definition": "Expected; caused by", "example": "The assignment is due Friday."},
    {"word": "Duty", "definition": "A moral or legal obligation", "example": "It is your duty to vote."},
    {"word": "Earn", "definition": "To receive money for work done", "example": "She earns a good salary."},
    {"word": "Educate", "definition": "To give knowledge or instruction", "example": "We must educate the next generation."},
    {"word": "Effect", "definition": "A result or change produced", "example": "The medicine had a positive effect."},
    {"word": "Effort", "definition": "Energy put into doing something", "example": "Success requires constant effort."},
    {"word": "Either", "definition": "One or the other of two", "example": "You can have either tea or coffee."},
    {"word": "Elect", "definition": "To choose by voting", "example": "They will elect a new leader."},
    {"word": "Embarrass", "definition": "To make someone feel self-conscious", "example": "Don't embarrass me in public."},
    {"word": "Emotion", "definition": "A strong feeling such as joy or sadness", "example": "She expressed her emotions openly."},
    {"word": "Encourage", "definition": "To give support and confidence", "example": "Teachers should encourage students."},
    {"word": "Endure", "definition": "To suffer through; to last", "example": "She endured years of hardship."},
    {"word": "Energy", "definition": "Power from sources like food or fuel", "example": "Exercise gives you more energy."},
    {"word": "Engage", "definition": "To involve or participate in", "example": "Engage with your community."},
    {"word": "Enjoy", "definition": "To take pleasure in something", "example": "I enjoy reading in the evening."},
    {"word": "Enormous", "definition": "Very large in size or amount", "example": "The building was enormous."},
    {"word": "Environment", "definition": "The surroundings in which one lives", "example": "We must protect the environment."},
    {"word": "Equal", "definition": "The same in quantity or value", "example": "Everyone deserves equal treatment."},
    {"word": "Essential", "definition": "Absolutely necessary", "example": "Water is essential for life."},
    {"word": "Establish", "definition": "To set up on a permanent basis", "example": "She established her own business."},
    {"word": "Estimate", "definition": "An approximate calculation", "example": "Give me an estimate of the cost."},
    {"word": "Evidence", "definition": "Facts that prove something", "example": "There is strong evidence of climate change."},
    {"word": "Exact", "definition": "Perfectly accurate", "example": "What is the exact time?"},
    {"word": "Examine", "definition": "To look at carefully", "example": "The doctor examined the patient."},
    {"word": "Excellent", "definition": "Extremely good", "example": "She did an excellent job."},
    {"word": "Except", "definition": "Not including; apart from", "example": "Everyone passed except Tom."},
    {"word": "Exist", "definition": "To have real being; to be present", "example": "Dinosaurs no longer exist."},
    {"word": "Expect", "definition": "To think something will happen", "example": "I expect good results."},
    {"word": "Experience", "definition": "Practical knowledge gained through doing", "example": "Work experience is valuable."},
    {"word": "Explain", "definition": "To make something clear", "example": "Please explain the rules."},
    {"word": "Express", "definition": "To show or communicate feelings", "example": "Express yourself clearly."},
    {"word": "Factor", "definition": "Something that affects a result", "example": "Diet is a major factor in health."},
    {"word": "Fail", "definition": "To not succeed", "example": "Don't be afraid to fail; learn from it."},
    {"word": "Fair", "definition": "Just and reasonable", "example": "That is a fair decision."},
    {"word": "Familiar", "definition": "Well-known; easy to recognize", "example": "That song sounds familiar."},
    {"word": "Famous", "definition": "Known by many people", "example": "She is a famous singer."},
    {"word": "Feature", "definition": "An important quality or characteristic", "example": "The main feature of the phone is its camera."},
    {"word": "Flexible", "definition": "Able to change or adapt easily", "example": "A flexible schedule is helpful."},
    {"word": "Focus", "definition": "To concentrate on something", "example": "Focus on what matters most."},
    {"word": "Formal", "definition": "Following official rules or customs", "example": "Wear formal clothes to the interview."},
    {"word": "Fortune", "definition": "Luck; a large amount of money", "example": "She made a fortune from her business."},
    {"word": "Frequent", "definition": "Happening often", "example": "He makes frequent visits to the gym."},
    {"word": "Friendly", "definition": "Kind and pleasant to others", "example": "She has a very friendly personality."},
    {"word": "Frustrate", "definition": "To cause feelings of annoyance", "example": "Traffic jams really frustrate me."},
    {"word": "Function", "definition": "The purpose or role of something", "example": "What is the function of this button?"},
    {"word": "Fundamental", "definition": "Basic and most important", "example": "Trust is fundamental in a relationship."},
    {"word": "Generate", "definition": "To produce or create", "example": "Solar panels generate electricity."},
    {"word": "Genuine", "definition": "Real and true; not fake", "example": "Is this a genuine diamond?"},
    {"word": "Global", "definition": "Relating to the whole world", "example": "Climate change is a global issue."},
    {"word": "Goal", "definition": "An aim or desired result", "example": "Set yourself clear goals."},
    {"word": "Govern", "definition": "To control and direct a country or group", "example": "Leaders must govern wisely."},
    {"word": "Gradually", "definition": "Slowly over time", "example": "She gradually improved her English."},
    {"word": "Grateful", "definition": "Feeling thankful", "example": "I am grateful for your help."},
    {"word": "Guarantee", "definition": "A promise that something will happen", "example": "The product comes with a one-year guarantee."},
    {"word": "Guide", "definition": "To show the way; a person who leads", "example": "The tour guide was very helpful."},
    {"word": "Habit", "definition": "Something done regularly", "example": "Reading daily is a good habit."},
    {"word": "Handle", "definition": "To deal with a situation", "example": "She handles pressure very well."},
    {"word": "Harm", "definition": "Physical or other damage", "example": "Smoking causes harm to your health."},
    {"word": "Harvest", "definition": "To gather a crop", "example": "Farmers harvest wheat in summer."},
    {"word": "Hesitate", "definition": "To pause before doing something", "example": "Don't hesitate to ask for help."},
    {"word": "Highlight", "definition": "To emphasize something important", "example": "Highlight the key points in your notes."},
    {"word": "Honest", "definition": "Truthful and without deceit", "example": "Always be honest with your friends."},
    {"word": "Honor", "definition": "High respect; to fulfill a commitment", "example": "It is an honor to meet you."},
    {"word": "Humble", "definition": "Not proud; having a modest view of oneself", "example": "Despite his success, he remained humble."},
    {"word": "Identify", "definition": "To recognize and name something", "example": "Can you identify the problem?"},
    {"word": "Ignore", "definition": "To pay no attention to", "example": "Don't ignore important warning signs."},
    {"word": "Impact", "definition": "A strong effect on someone or something", "example": "The new law had a big impact."},
    {"word": "Improve", "definition": "To make or become better", "example": "Practice helps you improve quickly."},
    {"word": "Include", "definition": "To contain as part of a whole", "example": "The price includes breakfast."},
    {"word": "Increase", "definition": "To become or make larger in amount", "example": "Sales increased by 20% this year."},
    {"word": "Indicate", "definition": "To point out or show", "example": "The sign indicates the exit."},
    {"word": "Individual", "definition": "A single person or thing", "example": "Each individual has a unique personality."},
    {"word": "Influence", "definition": "The power to affect others", "example": "Parents have a strong influence on children."},
    {"word": "Inform", "definition": "To give someone information", "example": "Please inform me of any changes."},
    {"word": "Initiative", "definition": "The ability to act without being told", "example": "Take initiative in your work."},
    {"word": "Innovate", "definition": "To introduce new ideas or methods", "example": "Companies must innovate to survive."},
    {"word": "Inspire", "definition": "To fill someone with motivation", "example": "Her speech inspired the whole team."},
    {"word": "Interpret", "definition": "To explain the meaning of something", "example": "How do you interpret this poem?"},
    {"word": "Involve", "definition": "To include as a part of something", "example": "The project involves a lot of research."},
    {"word": "Issue", "definition": "An important topic; a problem", "example": "Let's discuss the main issues."},
    {"word": "Journey", "definition": "A long trip from one place to another", "example": "Life is a journey, not a destination."},
    {"word": "Judgment", "definition": "The ability to make decisions wisely", "example": "Trust your own judgment."},
    {"word": "Justice", "definition": "Fairness in the way people are treated", "example": "Everyone deserves justice."},
    {"word": "Knowledge", "definition": "Facts or skills gained through experience", "example": "Knowledge is power."},
    {"word": "Language", "definition": "A system of communication", "example": "English is spoken all over the world."},
    {"word": "Launch", "definition": "To start or introduce something new", "example": "They will launch a new product next month."},
    {"word": "Lead", "definition": "To guide or be in charge", "example": "She was chosen to lead the team."},
    {"word": "Limit", "definition": "A point beyond which one cannot go", "example": "There is a limit to what I can do."},
    {"word": "Listen", "definition": "To pay attention to sounds", "example": "Listen carefully to instructions."},
    {"word": "Local", "definition": "Relating to a particular area", "example": "Support your local businesses."},
    {"word": "Logical", "definition": "Based on clear reasoning", "example": "That is a logical conclusion."},
    {"word": "Loyal", "definition": "Faithful to a person or cause", "example": "A loyal friend is hard to find."},
    {"word": "Maintain", "definition": "To keep in good condition", "example": "Maintain a healthy lifestyle."},
    {"word": "Manage", "definition": "To be in charge of; to cope with", "example": "She manages a large team."},
    {"word": "Manner", "definition": "A way of doing something; behavior", "example": "He spoke in a polite manner."},
    {"word": "Mature", "definition": "Fully developed; sensible", "example": "She is very mature for her age."},
    {"word": "Measure", "definition": "To find the size or amount of something", "example": "Measure the room before buying furniture."},
    {"word": "Method", "definition": "A particular way of doing something", "example": "What method do you use to study?"},
    {"word": "Minimum", "definition": "The least possible amount", "example": "The minimum age is 18."},
    {"word": "Mistake", "definition": "An action that is wrong or inaccurate", "example": "Everyone makes mistakes; learn from them."},
    {"word": "Modern", "definition": "Relating to the present time", "example": "Modern technology has changed our lives."},
    {"word": "Motive", "definition": "A reason for doing something", "example": "What was his motive for leaving?"},
    {"word": "Move", "definition": "To go from one place to another", "example": "We plan to move to a new city."},
    {"word": "Multiple", "definition": "More than one; many", "example": "She speaks multiple languages."},
    {"word": "Natural", "definition": "Existing in nature; not artificial", "example": "The park has beautiful natural scenery."},
    {"word": "Necessary", "definition": "Needed; required", "example": "It is necessary to drink water daily."},
    {"word": "Negotiate", "definition": "To reach an agreement through discussion", "example": "They negotiated a fair salary."},
    {"word": "Normal", "definition": "Usual; typical", "example": "It is normal to feel nervous."},
    {"word": "Notice", "definition": "To observe or become aware of", "example": "I didn't notice the mistake at first."},
    {"word": "Objective", "definition": "A goal; not influenced by personal feelings", "example": "What is the objective of this meeting?"},
    {"word": "Observe", "definition": "To watch carefully", "example": "Observe how the process works."},
    {"word": "Obtain", "definition": "To get something", "example": "How did you obtain this information?"},
    {"word": "Occur", "definition": "To happen", "example": "The accident occurred at noon."},
    {"word": "Opinion", "definition": "A personal view about something", "example": "In my opinion, this is the best solution."},
    {"word": "Opportunity", "definition": "A chance to do something", "example": "Take every opportunity to practice."},
    {"word": "Organize", "definition": "To arrange in a structured way", "example": "Organize your notes before studying."},
    {"word": "Original", "definition": "New and unique; the first version", "example": "Her ideas are always original."},
    {"word": "Overcome", "definition": "To succeed in dealing with a problem", "example": "She overcame many obstacles."},
    {"word": "Participate", "definition": "To take part in something", "example": "Participate actively in class."},
    {"word": "Patient", "definition": "Able to wait calmly; a sick person", "example": "Be patient; good things take time."},
    {"word": "Pattern", "definition": "A repeated design or sequence", "example": "I noticed a pattern in his behavior."},
    {"word": "Perform", "definition": "To carry out a task; to act", "example": "She performed well under pressure."},
    {"word": "Permission", "definition": "Official approval to do something", "example": "You need permission to enter."},
    {"word": "Persuade", "definition": "To convince someone to do something", "example": "He persuaded her to join the team."},
    {"word": "Plan", "definition": "A detailed proposal for doing something", "example": "Make a plan before you start."},
    {"word": "Positive", "definition": "Good; optimistic", "example": "Keep a positive attitude."},
    {"word": "Practice", "definition": "To do something repeatedly to improve", "example": "Practice English every day."},
    {"word": "Precise", "definition": "Exact and accurate", "example": "Give a precise answer."},
    {"word": "Prepare", "definition": "To make ready in advance", "example": "Prepare for the interview."},
    {"word": "Present", "definition": "To show or give; being here now", "example": "She presented her ideas clearly."},
    {"word": "Priority", "definition": "Something dealt with first in importance", "example": "Health should be your top priority."},
    {"word": "Problem", "definition": "A matter that is difficult to deal with", "example": "We need to solve this problem."},
    {"word": "Process", "definition": "A series of steps to achieve something", "example": "Follow the process carefully."},
    {"word": "Produce", "definition": "To make or create something", "example": "The factory produces 500 units daily."},
    {"word": "Progress", "definition": "Movement toward a goal", "example": "She is making great progress."},
    {"word": "Project", "definition": "A planned piece of work", "example": "The team finished the project on time."},
    {"word": "Promote", "definition": "To support or raise to a higher level", "example": "He was promoted to manager."},
    {"word": "Protect", "definition": "To keep safe from harm", "example": "Wear sunscreen to protect your skin."},
    {"word": "Provide", "definition": "To give something needed", "example": "The school provides free meals."},
    {"word": "Purpose", "definition": "The reason something is done", "example": "What is the purpose of this exercise?"},
    {"word": "Quality", "definition": "The standard of something; how good it is", "example": "Focus on quality, not quantity."},
    {"word": "Question", "definition": "A sentence that asks for information", "example": "Ask questions when you are unsure."},
    {"word": "Quick", "definition": "Done in a short time; fast", "example": "She gave a quick response."},
    {"word": "Realize", "definition": "To become aware of something", "example": "I realized I had made a mistake."},
    {"word": "Reason", "definition": "A cause or explanation", "example": "Give me a reason to trust you."},
    {"word": "Recognize", "definition": "To identify from past experience", "example": "I recognized her voice immediately."},
    {"word": "Reduce", "definition": "To make smaller in size or amount", "example": "Reduce waste by recycling."},
    {"word": "Reflect", "definition": "To think deeply; to show an image", "example": "Take time to reflect on your choices."},
    {"word": "Relate", "definition": "To connect; to understand someone", "example": "I can relate to your experience."},
    {"word": "Reliable", "definition": "Consistently good; dependable", "example": "She is a reliable employee."},
    {"word": "Replace", "definition": "To put something new in place of another", "example": "Replace the old batteries."},
    {"word": "Require", "definition": "To need something", "example": "This job requires experience."},
    {"word": "Research", "definition": "Careful study to find information", "example": "Good research supports strong arguments."},
    {"word": "Resolve", "definition": "To find a solution to a problem", "example": "Let's resolve this issue quickly."},
    {"word": "Respect", "definition": "High regard for someone or something", "example": "Treat others with respect."},
    {"word": "Respond", "definition": "To say or act in reply", "example": "Please respond to my email."},
    {"word": "Responsible", "definition": "Being in charge; having good judgment", "example": "Be responsible with your money."},
    {"word": "Result", "definition": "The outcome of something", "example": "What was the result of the experiment?"},
    {"word": "Review", "definition": "To examine or assess something", "example": "Review your notes before the test."},
    {"word": "Risk", "definition": "A situation involving possible danger", "example": "Every business involves some risk."},
    {"word": "Role", "definition": "The part played by someone", "example": "Parents play a key role in education."},
    {"word": "Safe", "definition": "Protected from danger or risk", "example": "Always keep children safe."},
    {"word": "Satisfy", "definition": "To meet needs or expectations", "example": "The meal satisfied everyone."},
    {"word": "Schedule", "definition": "A plan of activities with times", "example": "Follow a daily schedule."},
    {"word": "Select", "definition": "To choose carefully", "example": "Select the best answer."},
    {"word": "Sensitive", "definition": "Quick to detect or respond; easily affected", "example": "She is sensitive to criticism."},
    {"word": "Serious", "definition": "Demanding attention; not joking", "example": "This is a serious matter."},
    {"word": "Share", "definition": "To use or give jointly", "example": "Share your knowledge with others."},
    {"word": "Significant", "definition": "Important; large enough to be noticed", "example": "There was a significant improvement."},
    {"word": "Simple", "definition": "Easy to understand or do", "example": "Keep your explanation simple."},
    {"word": "Situation", "definition": "A set of circumstances", "example": "It was a difficult situation."},
    {"word": "Skill", "definition": "The ability to do something well", "example": "Reading is an important skill."},
    {"word": "Solve", "definition": "To find the answer to a problem", "example": "Can you solve this equation?"},
    {"word": "Source", "definition": "Where something comes from", "example": "What is your source of information?"},
    {"word": "Specific", "definition": "Clearly defined; precise", "example": "Be specific about what you want."},
    {"word": "Standard", "definition": "A level of quality used as a measure", "example": "Maintain a high standard of work."},
    {"word": "Strategy", "definition": "A plan to achieve a goal", "example": "We need a better marketing strategy."},
    {"word": "Strengthen", "definition": "To make stronger", "example": "Exercise strengthens your muscles."},
    {"word": "Structure", "definition": "The way something is built or organized", "example": "The report needs a clear structure."},
    {"word": "Study", "definition": "To apply the mind to learn", "example": "Study for at least one hour daily."},
    {"word": "Succeed", "definition": "To achieve a desired result", "example": "Work hard and you will succeed."},
    {"word": "Suggest", "definition": "To put forward an idea", "example": "I suggest we start early."},
    {"word": "Support", "definition": "To help or assist", "example": "Support your team members."},
    {"word": "Survive", "definition": "To continue to live or exist", "example": "How do people survive extreme cold?"},
    {"word": "Task", "definition": "A piece of work to be done", "example": "Complete each task before moving on."},
    {"word": "Temporary", "definition": "Lasting for only a short time", "example": "This is only a temporary solution."},
    {"word": "Tend", "definition": "To regularly behave in a certain way", "example": "She tends to arrive early."},
    {"word": "Thankful", "definition": "Feeling or expressing gratitude", "example": "I am thankful for this opportunity."},
    {"word": "Theory", "definition": "A set of ideas to explain something", "example": "Darwin's theory of evolution."},
    {"word": "Thorough", "definition": "Complete with great attention to detail", "example": "Do a thorough check before submitting."},
    {"word": "Thoughtful", "definition": "Showing consideration for others", "example": "It was thoughtful of you to call."},
    {"word": "Tolerate", "definition": "To allow or accept something unpleasant", "example": "I cannot tolerate rudeness."},
    {"word": "Transfer", "definition": "To move from one place to another", "example": "Transfer the files to the new computer."},
    {"word": "Transform", "definition": "To make a thorough change", "example": "Exercise can transform your body."},
    {"word": "Trust", "definition": "Firm belief in someone's honesty", "example": "Trust must be earned over time."},
    {"word": "Truth", "definition": "A fact that is accepted as real", "example": "Always tell the truth."},
    {"word": "Unique", "definition": "Being the only one of its kind", "example": "Everyone's fingerprint is unique."},
    {"word": "Update", "definition": "To make something more modern", "example": "Update your software regularly."},
    {"word": "Urgent", "definition": "Requiring immediate action", "example": "This is an urgent matter."},
    {"word": "Useful", "definition": "Able to be used for a practical purpose", "example": "English is a useful language to know."},
    {"word": "Valid", "definition": "Legally or officially acceptable", "example": "You need a valid passport to travel."},
    {"word": "Value", "definition": "The importance or worth of something", "example": "Hard work has real value."},
    {"word": "Various", "definition": "Different; of many kinds", "example": "There are various ways to learn."},
    {"word": "Vision", "definition": "The ability to think about the future", "example": "She had a clear vision for the company."},
    {"word": "Volunteer", "definition": "To offer to do something without pay", "example": "I volunteer at the local shelter."},
    {"word": "Wealth", "definition": "A large amount of money or assets", "example": "Wealth brings responsibility."},
    {"word": "Willing", "definition": "Ready to do something", "example": "Are you willing to work overtime?"},
    {"word": "Wisdom", "definition": "Knowledge and good judgment", "example": "With age comes wisdom."},
    {"word": "Wonder", "definition": "A feeling of amazement; to think about", "example": "I wonder what will happen next."},
    {"word": "Worry", "definition": "To feel anxious about something", "example": "Don't worry; everything will be fine."},
    {"word": "Absolute", "definition": "Complete and total", "example": "That is the absolute truth."},
    {"word": "Abstract", "definition": "Existing as an idea, not physical", "example": "Love is an abstract concept."},
    {"word": "Access", "definition": "The right or opportunity to use something", "example": "Students have access to the library."},
    {"word": "Account", "definition": "A record of money; to explain", "example": "Open a bank account today."},
    {"word": "Affect", "definition": "To have an impact on something", "example": "Stress can affect your health."},
    {"word": "Agent", "definition": "A person who acts on behalf of another", "example": "She hired a travel agent."},
    {"word": "Aid", "definition": "Help or support given", "example": "First aid can save lives."},
    {"word": "Aim", "definition": "A goal or purpose", "example": "My aim is to speak fluently."},
    {"word": "Alternative", "definition": "Another option available", "example": "Is there an alternative route?"},
    {"word": "Analyze", "definition": "To examine in detail", "example": "Analyze the data carefully."},
    {"word": "Apply", "definition": "To make a formal request; to use", "example": "Apply for the job today."},
    {"word": "Appreciate", "definition": "To recognize the value of something", "example": "I appreciate your support."},
    {"word": "Approve", "definition": "To officially agree to something", "example": "The manager approved the plan."},
    {"word": "Area", "definition": "A region or part of a place", "example": "This is a safe area to live."},
    {"word": "Aspect", "definition": "A particular part or feature", "example": "Consider every aspect of the decision."},
    {"word": "Assess", "definition": "To evaluate or judge something", "example": "Assess your progress every month."},
    {"word": "Associate", "definition": "To connect things in one's mind", "example": "I associate summer with holidays."},
    {"word": "Attribute", "definition": "A quality or feature; to credit", "example": "She attributes her success to hard work."},
    {"word": "Base", "definition": "The bottom part; a foundation", "example": "Build a strong base of knowledge."},
    {"word": "Basis", "definition": "A foundation or starting point", "example": "On what basis did you make that choice?"},
    {"word": "Behavior", "definition": "The way a person acts", "example": "Good behavior is always rewarded."},
    {"word": "Category", "definition": "A group of similar things", "example": "Books are grouped into categories."},
    {"word": "Circumstance", "definition": "A fact connected with an event", "example": "Under no circumstance should you give up."},
    {"word": "Comment", "definition": "A remark expressing an opinion", "example": "Leave a comment below the post."},
    {"word": "Communicate", "definition": "To share information with others", "example": "Communicate clearly and confidently."},
    {"word": "Community", "definition": "A group of people living together", "example": "Give back to your community."},
    {"word": "Conclude", "definition": "To bring to an end; to decide", "example": "What do you conclude from this data?"},
    {"word": "Condition", "definition": "The state of something; a requirement", "example": "The condition of the car was excellent."},
    {"word": "Conduct", "definition": "The way someone behaves; to lead", "example": "His conduct was professional."},
    {"word": "Conflict", "definition": "A serious disagreement", "example": "Try to resolve conflict peacefully."},
    {"word": "Consequence", "definition": "A result of an action", "example": "Think about the consequences before acting."},
    {"word": "Consist", "definition": "To be made up of", "example": "The team consists of ten players."},
    {"word": "Constant", "definition": "Happening all the time", "example": "There is constant noise outside."},
    {"word": "Contribute", "definition": "To give a share to a common effort", "example": "Everyone must contribute to the project."},
    {"word": "Cooperate", "definition": "To work together toward a goal", "example": "Cooperate with your classmates."},
    {"word": "Cope", "definition": "To deal with difficulties", "example": "She learned to cope with stress."},
    {"word": "Critical", "definition": "Extremely important; expressing disapproval", "example": "Critical thinking is a key skill."},
    {"word": "Current", "definition": "Happening or existing now", "example": "What is your current job?"},
    {"word": "Deadline", "definition": "The latest time for completing something", "example": "Submit the report before the deadline."},
    {"word": "Decision", "definition": "A conclusion reached after consideration", "example": "Make decisions based on facts."},
    {"word": "Depend", "definition": "To rely on someone or something", "example": "Children depend on their parents."},
    {"word": "Detail", "definition": "A small individual item of information", "example": "Pay attention to every detail."},
    {"word": "Determine", "definition": "To cause or control; to find out", "example": "Effort determines success."},
    {"word": "Diverse", "definition": "Showing a great deal of variety", "example": "Our team is diverse and talented."},
    {"word": "Dominant", "definition": "Most important or powerful", "example": "English is the dominant language in business."},
    {"word": "Efficient", "definition": "Achieving results with minimum waste", "example": "She is an efficient worker."},
    {"word": "Eliminate", "definition": "To completely remove something", "example": "Eliminate bad habits one by one."},
    {"word": "Emphasize", "definition": "To give special importance to something", "example": "Emphasize your key points."},
    {"word": "Enable", "definition": "To make something possible", "example": "Technology enables us to work from home."},
    {"word": "Encounter", "definition": "To meet unexpectedly", "example": "I encountered a problem with the software."},
    {"word": "Enhance", "definition": "To improve the quality of something", "example": "Good design enhances the user experience."},
    {"word": "Ensure", "definition": "To make certain something happens", "example": "Ensure the door is locked before leaving."},
    {"word": "Evaluate", "definition": "To form an idea about the value of something", "example": "Evaluate your progress weekly."},
    {"word": "Expand", "definition": "To become larger or more extensive", "example": "The company plans to expand overseas."},
    {"word": "Expose", "definition": "To reveal; to put in contact with", "example": "Travel exposes you to new cultures."},
    {"word": "Extend", "definition": "To make longer or wider", "example": "We can extend the deadline by one week."},
    {"word": "Extract", "definition": "To remove or take out", "example": "Extract the key information from the text."},
    {"word": "Fund", "definition": "Money for a specific purpose", "example": "The project needs more funding."},
    {"word": "Gain", "definition": "To obtain something desirable", "example": "Gain confidence by practicing daily."},
    {"word": "Gap", "definition": "A space or difference between two things", "example": "Bridge the gap between theory and practice."},
    {"word": "Gather", "definition": "To collect or come together", "example": "Gather information before writing."},
    {"word": "Grasp", "definition": "To seize and hold; to understand", "example": "It took time to grasp the concept."},
    {"word": "Growth", "definition": "The process of increasing", "example": "Personal growth requires effort."},
    {"word": "Image", "definition": "A picture or representation", "example": "Your public image matters."},
    {"word": "Implement", "definition": "To put a plan into action", "example": "Implement the new policy immediately."},
    {"word": "Imply", "definition": "To suggest without saying directly", "example": "What does this sentence imply?"},
    {"word": "Instance", "definition": "An example of something", "example": "For instance, consider this situation."},
    {"word": "Instruct", "definition": "To teach or direct someone", "example": "The teacher instructed the students."},
    {"word": "Integrate", "definition": "To combine into a whole", "example": "Integrate new vocabulary into your speech."},
    {"word": "Intense", "definition": "Extreme in degree or strength", "example": "The training was very intense."},
    {"word": "Interact", "definition": "To act in a way that affects others", "example": "Interact with native speakers daily."},
    {"word": "Introduce", "definition": "To bring in something for the first time", "example": "Let me introduce myself."},
    {"word": "Investigate", "definition": "To examine carefully to find facts", "example": "The police will investigate the case."},
    {"word": "Join", "definition": "To become part of a group", "example": "Join a club to meet new people."},
    {"word": "Label", "definition": "A tag with information; to classify", "example": "Label all your folders clearly."},
    {"word": "Lack", "definition": "The absence of something needed", "example": "A lack of sleep affects concentration."},
    {"word": "Link", "definition": "A connection between two things", "example": "There is a clear link between exercise and health."},
    {"word": "Location", "definition": "A particular place or position", "example": "What is the location of the office?"},
    {"word": "Logic", "definition": "Reasoning in a clear and consistent way", "example": "Use logic to solve the problem."},
    {"word": "Major", "definition": "Important; greater in size", "example": "This is a major decision."},
    {"word": "Majority", "definition": "More than half of a total", "example": "The majority voted in favor."},
    {"word": "Maximize", "definition": "To make as large as possible", "example": "Maximize your study time."},
    {"word": "Meaningful", "definition": "Having purpose or significance", "example": "Have meaningful conversations."},
    {"word": "Mental", "definition": "Relating to the mind", "example": "Mental health is just as important as physical health."},
    {"word": "Mention", "definition": "To refer to briefly", "example": "She mentioned a new idea."},
    {"word": "Model", "definition": "An example to follow; a representation", "example": "She is a role model for students."},
    {"word": "Monitor", "definition": "To observe and check progress", "example": "Monitor your spending carefully."},
    {"word": "Motivate", "definition": "To provide a reason to do something", "example": "Good teachers motivate their students."},
    {"word": "Mutual", "definition": "Shared by two or more parties", "example": "We reached a mutual agreement."},
    {"word": "Outcome", "definition": "The way something turns out", "example": "A positive outcome requires consistent effort."},
    {"word": "Output", "definition": "The amount of something produced", "example": "Increase your daily output."},
    {"word": "Overall", "definition": "Taken as a whole", "example": "Overall, the event was a success."},
    {"word": "Overlap", "definition": "To cover part of the same area", "example": "Our interests overlap in many areas."},
    {"word": "Pace", "definition": "The speed at which something happens", "example": "Work at your own pace."},
    {"word": "Perceive", "definition": "To understand or interpret something", "example": "How do you perceive this situation?"},
    {"word": "Perspective", "definition": "A point of view", "example": "Look at things from a different perspective."},
    {"word": "Phase", "definition": "A distinct stage in a process", "example": "We are entering a new phase."},
    {"word": "Physical", "definition": "Relating to the body", "example": "Physical exercise improves mood."},
    {"word": "Potential", "definition": "The capacity to develop into something", "example": "You have great potential."},
    {"word": "Practical", "definition": "Relating to real situations; useful", "example": "Practical skills are essential in life."},
    {"word": "Predict", "definition": "To say what will happen in the future", "example": "Can you predict tomorrow's weather?"},
    {"word": "Principle", "definition": "A basic rule or belief", "example": "Honesty is a core principle."},
    {"word": "Proceed", "definition": "To begin or continue an action", "example": "Proceed with caution."},
    {"word": "Profit", "definition": "Money gained from a business", "example": "The company made a large profit."},
    {"word": "Propose", "definition": "To suggest a plan or idea", "example": "She proposed a new solution."},
    {"word": "Prove", "definition": "To demonstrate something is true", "example": "Prove your argument with evidence."},
    {"word": "Publish", "definition": "To make content available to the public", "example": "She published her first book."},
    {"word": "Range", "definition": "A variety; the extent of something", "example": "The shop has a wide range of products."},
    {"word": "Rapid", "definition": "Happening in a short time; fast", "example": "Rapid changes are happening in technology."},
    {"word": "Realistic", "definition": "Based on facts; achievable", "example": "Set realistic goals."},
    {"word": "Recall", "definition": "To remember something", "example": "I can't recall where I put my keys."},
    {"word": "Refer", "definition": "To mention or direct attention to", "example": "Refer to the glossary for definitions."},
    {"word": "Region", "definition": "An area with common features", "example": "The tropical region has heavy rainfall."},
    {"word": "Reinforce", "definition": "To strengthen or support", "example": "Reinforce your learning by reviewing notes."},
    {"word": "Relevant", "definition": "Closely connected to the matter at hand", "example": "Provide relevant examples in your essay."},
    {"word": "Represent", "definition": "To act or speak on behalf of", "example": "She represents the school at competitions."},
    {"word": "Resource", "definition": "A stock or supply that can be used", "example": "Use all available resources wisely."},
    {"word": "Reveal", "definition": "To make previously hidden things known", "example": "The investigation revealed the truth."},
    {"word": "Revise", "definition": "To reconsider and amend something", "example": "Revise your essay before submitting."},
    {"word": "Reward", "definition": "Something given in recognition of effort", "example": "Hard work brings its own rewards."},
    {"word": "Scene", "definition": "The place where something occurs", "example": "Police arrived at the scene quickly."},
    {"word": "Seek", "definition": "To search for or try to find", "example": "Seek help when you need it."},
    {"word": "Sense", "definition": "A feeling; one of the five senses", "example": "She has a great sense of humor."},
    {"word": "Sequence", "definition": "A particular order of things", "example": "Follow the steps in sequence."},
    {"word": "Settle", "definition": "To resolve; to make a home somewhere", "example": "They settled in Cape Town."},
    {"word": "Social", "definition": "Relating to society or companionship", "example": "Social skills are important in the workplace."},
    {"word": "Stable", "definition": "Not likely to change or fail", "example": "A stable income is reassuring."},
    {"word": "State", "definition": "A condition; to say something", "example": "Please state your name clearly."},
    {"word": "Stress", "definition": "Pressure or tension; to emphasize", "example": "Manage stress through exercise and rest."},
    {"word": "Submit", "definition": "To hand in for consideration", "example": "Submit your application before the deadline."},
    {"word": "Sufficient", "definition": "Enough for the purpose", "example": "Is there sufficient time to finish?"},
    {"word": "Summarize", "definition": "To give a brief statement of main points", "example": "Summarize the article in one paragraph."},
    {"word": "Symbol", "definition": "A sign that represents something", "example": "The dove is a symbol of peace."},
    {"word": "Target", "definition": "An aim or objective", "example": "Set a target and work toward it."},
    {"word": "Technique", "definition": "A particular way of doing something", "example": "Use this technique to improve your writing."},
    {"word": "Tendency", "definition": "An inclination to act in a certain way", "example": "He has a tendency to speak too fast."},
    {"word": "Term", "definition": "A word or phrase; a period of time", "example": "Define the key terms in the essay."},
    {"word": "Theme", "definition": "The main subject of a text or discussion", "example": "What is the theme of the story?"},
    {"word": "Tidy", "definition": "Neat and organized", "example": "Keep your workspace tidy."},
    {"word": "Track", "definition": "To follow progress; a path", "example": "Track your daily vocabulary progress."},
    {"word": "Trend", "definition": "A general development or change", "example": "Online learning is a growing trend."},
    {"word": "Ultimate", "definition": "Final; most extreme", "example": "Success is the ultimate goal."},
    {"word": "Underline", "definition": "To mark; to emphasize importance", "example": "Underline the key vocabulary."},
    {"word": "Undertake", "definition": "To commit to doing something", "example": "She undertook the challenge with confidence."},
    {"word": "Uniform", "definition": "The same throughout; a standard outfit", "example": "Students wear a uniform to school."},
    {"word": "Unite", "definition": "To come together as one", "example": "Sports can unite people."},
    {"word": "Universal", "definition": "Applying to all cases", "example": "Music is a universal language."},
    {"word": "Utilize", "definition": "To make practical use of something", "example": "Utilize every opportunity to practice."},
    {"word": "Vary", "definition": "To change; to be different", "example": "Prices vary from shop to shop."},
    {"word": "Vast", "definition": "Of very great extent or quantity", "example": "The ocean is vast."},
    {"word": "Verify", "definition": "To make sure something is true", "example": "Verify the information before sharing it."},
    {"word": "Version", "definition": "A form of something that differs slightly", "example": "Download the latest version of the app."},
    {"word": "View", "definition": "An opinion; what you see", "example": "What is your view on this issue?"},
    {"word": "Vital", "definition": "Absolutely necessary; essential", "example": "Sleep is vital for good health."},
    {"word": "Vocabulary", "definition": "All the words a person knows", "example": "Building your vocabulary takes time."},
    {"word": "Volume", "definition": "Quantity; the loudness of sound", "example": "Turn up the volume."},
    {"word": "Widespread", "definition": "Found or distributed over a large area", "example": "There is widespread support for the plan."},
    {"word": "Withdraw", "definition": "To take out; to leave a place", "example": "He withdrew money from the bank."},
    {"word": "Worth", "definition": "Equal in value to; merit", "example": "Is it worth the effort?"},
]


# ── RANDOM WORD OF THE DAY (seeded by date — same word for all users each day) ─
def get_today_word():
    today = datetime.now()
    seed = today.year * 10000 + today.month * 100 + today.day
    x = math.sin(seed + 1) * 10000
    index = int((x - int(x)) * len(words))
    return words[index]


# ── KEYBOARDS ──────────────────────────────────────────────────────────────────
def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📖 Word of the Day", callback_data="word_of_the_day")],
        [InlineKeyboardButton("📅 Book a Lesson", callback_data="book_lesson")],
        [InlineKeyboardButton("👩‍🏫 About Me", callback_data="about_me")],
        [InlineKeyboardButton("✉️ Message the Teacher", callback_data="message_teacher")],
        [InlineKeyboardButton("🔔 Weekly Reminders", callback_data="notifications_menu")],
    ])

def back_button():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Back to Menu", callback_data="back_to_menu")]])


# ── /start ────────────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    name = update.effective_user.first_name or "there"
    if chat_id not in subscribers:
        subscribers[chat_id] = {"name": name, "subscribed": False, "awaiting_message": False}
    await update.message.reply_text(
        f"👋 Hello, {name}! Welcome to the *Creative Alignmentz English Bot*! 🎉\n\nChoose an option below to get started:",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(),
    )


# ── CALLBACK HANDLER ──────────────────────────────────────────────────────────
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id
    data = query.data

    if data == "word_of_the_day":
        w = get_today_word()
        today_str = datetime.now().strftime("%A, %d %B %Y")
        await query.message.reply_text(
            f"📖 *Word of the Day*\n_{today_str}_\n\n"
            f"🔤 *{w['word']}*\n\n"
            f"📝 *Definition:*\n{w['definition']}\n\n"
            f"💬 *Example:*\n_{w['example']}_\n\n"
            f"Keep learning — one word at a time! 💪",
            parse_mode="Markdown",
            reply_markup=back_button(),
        )

    elif data == "book_lesson":
        await query.message.reply_text(
            "📅 *Book a Lesson*\n\nReady to take your English to the next level? "
            "Click below to book a 1-on-1 lesson with me at a time that suits you! 🎓",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📆 Open Booking Calendar", url=CALENDAR_URL)],
                [InlineKeyboardButton("🏠 Back to Menu", callback_data="back_to_menu")],
            ]),
        )

    elif data == "about_me":
        await query.message.reply_text(
            "👩‍🏫 *About Me*\n\nI am a qualified English teacher passionate about helping people "
            "communicate with confidence! 🌍\n\nVisit my website to learn more about my teaching "
            "style, experience, and what my students say.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🌐 Visit My Website", url=WEBSITE_URL)],
                [InlineKeyboardButton("🏠 Back to Menu", callback_data="back_to_menu")],
            ]),
        )

    elif data == "message_teacher":
        user = subscribers.setdefault(chat_id, {"name": "", "subscribed": False, "awaiting_message": False})
        user["awaiting_message"] = True
        await query.message.reply_text(
            "✉️ *Message the Teacher*\n\nType your message below and send it — "
            "I will get back to you as soon as possible! 😊\n\n_Type your message now:_",
            parse_mode="Markdown",
            reply_markup=back_button(),
        )

    elif data == "notifications_menu":
        user = subscribers.get(chat_id, {})
        is_on = user.get("subscribed", False)
        status = "✅ *ON*" if is_on else "❌ *OFF*"
        toggle_text = "🔕 Turn Off Reminders" if is_on else "🔔 Turn On Reminders"
        toggle_data = "notif_off" if is_on else "notif_on"
        await query.message.reply_text(
            f"🔔 *Weekly Reminders*\n\nGet a reminder every Monday to book your next English lesson "
            f"and keep your progress going! 📚\n\nStatus: {status}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(toggle_text, callback_data=toggle_data)],
                [InlineKeyboardButton("🏠 Back to Menu", callback_data="back_to_menu")],
            ]),
        )

    elif data == "notif_on":
        user = subscribers.setdefault(chat_id, {"name": "", "subscribed": False, "awaiting_message": False})
        user["subscribed"] = True
        await query.message.reply_text(
            "✅ *Reminders are ON!*\n\nYou will receive a weekly reminder every Monday to book your "
            "next lesson. See you in class! 🎓",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📆 Book a Lesson Now", url=CALENDAR_URL)],
                [InlineKeyboardButton("🏠 Back to Menu", callback_data="back_to_menu")],
            ]),
        )

    elif data == "notif_off":
        user = subscribers.setdefault(chat_id, {"name": "", "subscribed": False, "awaiting_message": False})
        user["subscribed"] = False
        await query.message.reply_text(
            "🔕 *Reminders are OFF.*\n\nYou won't receive weekly reminders anymore. "
            "You can always turn them back on from the menu.",
            parse_mode="Markdown",
            reply_markup=back_button(),
        )

    elif data == "back_to_menu":
        user = subscribers.get(chat_id, {})
        user["awaiting_message"] = False
        await query.message.reply_text(
            "🏠 *Main Menu*\n\nWhat would you like to do?",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard(),
        )


# ── HANDLE STUDENT MESSAGES ───────────────────────────────────────────────────
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = subscribers.get(chat_id, {})

    if user.get("awaiting_message"):
        user["awaiting_message"] = False
        sender_name = update.effective_user.first_name or "A student"
        sender_username = f"@{update.effective_user.username}" if update.effective_user.username else "no username"
        sender_id = update.effective_user.id

        await update.message.reply_text(
            "✅ *Message sent!*\n\nThank you! I will reply as soon as possible. 😊",
            parse_mode="Markdown",
            reply_markup=back_button(),
        )

        if TEACHER_CHAT_ID:
            await context.bot.send_message(
                chat_id=TEACHER_CHAT_ID,
                text=(
                    f"📩 *New Student Message!*\n\n"
                    f"👤 *From:* {sender_name} ({sender_username})\n"
                    f"🆔 *Chat ID:* {sender_id}\n\n"
                    f"💬 *Message:*\n{update.message.text}\n\n"
                    f"_Reply directly to this chat ID to respond._"
                ),
                parse_mode="Markdown",
            )
    else:
        await update.message.reply_text(
            "👇 Use the menu below to explore!",
            reply_markup=main_menu_keyboard(),
        )


# ── WEEKLY REMINDER JOB (runs every Monday at 9:00 AM) ───────────────────────
async def send_weekly_reminders(context: ContextTypes.DEFAULT_TYPE):
    for chat_id, user in subscribers.items():
        if user.get("subscribed"):
            name = user.get("name") or "there"
            try:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=(
                        f"🔔 *Weekly Reminder!*\n\n"
                        f"Hey {name}! 👋\n\n"
                        f"A new week is here — don't forget to book your English lesson! "
                        f"Consistent practice is the key to fluency. 🗝️\n\n"
                        f"Book now and keep moving forward! 🚀"
                    ),
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("📆 Book My Lesson Now", url=CALENDAR_URL)],
                        [InlineKeyboardButton("🔕 Turn Off Reminders", callback_data="notif_off")],
                    ]),
                )
            except Exception as e:
                logger.warning(f"Could not send reminder to {chat_id}: {e}")


# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Schedule weekly reminder every Monday at 09:00
    app.job_queue.run_daily(
        send_weekly_reminders,
        time=time(hour=9, minute=0, second=0),
        days=(0,),  # 0 = Monday in python-telegram-bot
    )

    print("✅ Creative Alignmentz English Bot is running!")
    app.run_polling()


if __name__ == "__main__":
    main()
