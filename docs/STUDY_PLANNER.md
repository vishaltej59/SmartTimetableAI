# Study Planner Core Algorithm

The `planner_service.py` is the algorithmic core of the Smart Timetable AI. It handles the mathematical distribution of preparation time and identifies free gaps in the user's schedule using the Google Calendar API.

---

## 1. Mathematical Weight Distribution

Instead of distributing hours evenly across all remaining days, the planner assumes that learning intensity should increase closer to the exam date (preventing early decay of memory and aligning with natural study cycles).

The algorithm calculates the daily hour allocation as follows:
- Let $D$ be the number of days remaining until the exam.
- The weight for each day $i$ (where $i = 1$ is tomorrow, and $i = D$ is the exam eve) is defined as $W_i = i$.
- The total weight is the sum of arithmetic progression: 
  $$\text{Total Weight} = \sum_{j=1}^{D} j = \frac{D(D + 1)}{2}$$
- The target hours allocated to Day $i$ is:
  $$\text{Target Hours}_i = \text{Total Preparation Hours Required} \times \left(\frac{W_i}{\text{Total Weight}}\right)$$

*Note: If the exam is today or tomorrow, the algorithm falls back to allocating 100% of the preparation hours to the single remaining day (capped at a maximum of 14 hours per day, rolling over any excess hours).*

---

## 2. Conflict-Free Gap Finding Algorithm

To determine exactly when the student has free time, the algorithm performs the following calculations:

1. **Active Boundary Enforcement:** For any target day, the planner only schedules study slots between a customizable time envelope, defaulting to **8:00 AM to 10:00 PM (14 hours max)**.
2. **Retrieve Calendar Overlaps:** The algorithm retrieves the user's active Google Calendar events and extracts their exact `start` and `end` times.
3. **Merge Overlapping Commits:**
   To handle overlapping calendar events, the system merges them:
   - Sort all events by start time.
   - Iterate through the list. If the current event starts before the previous event ends, merge them by extending the previous event's end time to the maximum of both.
4. **Determine Free Windows:**
   - The system checks the gaps between the merged events within the 8:00 AM to 10:00 PM envelope.
   - Any gap that is equal to or larger than the minimum threshold (default **30 minutes**) is marked as an available study slot.

---

## 3. Session Sub-Chunking and Burnout Protection

To promote cognitive focus, the planner applies strict constraints to the found free slots:

- **Focus Cap:** Any contiguous free slot is divided into chunks of at most **2 hours**.
- **Study vs. Revision Split:** 
  - The first **70%** of the scheduled hours are designated as **"Study: [Subject]"** (focusing on learning new concepts).
  - The remaining **30%** of the scheduled hours are labeled as **"Revision: [Subject]"** (focusing on mock questions and active recall).
- **Mandatory Break Injection:**
  - After a study chunk, the algorithm inserts a **15-minute break**.
  - If the free slot does not have at least 15 minutes remaining after a break is added, no further sessions are scheduled in that specific gap.

---

## 4. Rollover & Quality Scoring

- **Rollover:** If a day's target hours cannot be fully scheduled due to calendar conflicts, the remaining unscheduled hours are rolled over to the next day's allocation.
- **Quality Score:**
  After completing the plan generation, the planner computes a **Quality Score** based on the final coverage of requested preparation hours:
  - **$\ge 95\%$ coverage:** Excellent ⭐
  - **$\ge 80\%$ coverage:** Good 👍
  - **$\ge 60\%$ coverage:** Fair ⚠️
  - **$< 60\%$ coverage:** Poor ❌ (indicates severe calendar congestion requiring rescheduling)
