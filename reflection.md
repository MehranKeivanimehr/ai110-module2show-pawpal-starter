# PawPal+ Project Reflection

## 1. System Design

PawPal+ is designed to help a pet owner organize and plan daily pet care activities.

Three core actions the user should be able to perform are:

    1-1. The user should be able to enter and manage basic owner and pet information so the system can support personalized care planning.

    1-2. The user should be able to add, edit, and organize pet care tasks such as feeding, walks, medication, grooming, and enrichment, including important details like duration and priority.

    1-3. The user should be able to generate and review a daily care plan based on task importance, available time, and owner preferences, while also seeing why the plan was selected.


**a. Initial design**

- Briefly describe your initial UML design.
My initial UML design for PawPal+ was kept simple and focused on the main parts of the app. I included four classes: Owner, Pet, Task, and Scheduler. The relationships were straightforward: an Owner can have multiple Pets, each Pet can have multiple Tasks, and the Scheduler works with tasks to build a daily plan.

- What classes did you include, and what responsibilities did you assign to each?
The Owner class was responsible for storing user information such as name, available time, preferences, and the pets they manage. The Pet class represented each pet and held basic details like name, species, age, notes, and its task list. The Task class represented individual care activities such as feeding, walks, medication, or grooming, along with details like duration, priority, due time, recurring status, and completion status. The Scheduler class was responsible for organizing tasks, checking conflicts, and generating a daily schedule based on time and priority.

**b. Design changes**

- Did your design change during implementation?

Yes, the design changed slightly after reviewing the class skeleton.

- If yes, describe at least one change and why you made it.

The main change was in the Scheduler class. In the initial design, Scheduler stored its own available_time and task list. After review, I changed it so that Scheduler works directly with the Owner object instead. This avoids duplicated data and makes it easier for the scheduler to access pets and their tasks when building a daily plan.

I also updated Task.update_task() so it can accept changes more flexibly, and I replaced the raw task status string with a small enum to keep task states more consistent.
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
