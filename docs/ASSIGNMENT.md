# SDE Intern Assignment - Deepsolv

## Guidelines
- You can use Python for implementing the solution. You may choose FastAPI/Django/Flask or any other Server framework for creating a Web Server.
- You would need to use a database (MySQL/ MongoDB) for persistent storage.
- Your APIs should be well tested and should be in a demo-able state. You will be asked to run these APIs after this assignment.
- Use of AI or any kind of plagiarism is STRICTLY PROHIBITED, if detected by our systems, your Application will be straightaway rejected automatically.
- The focus should be on developing a robust, scalable, and maintainable backend system.
- Candidates should adhere to best practices in software development, including OOP principles, SOLID design patterns, clean code, and RESTful API design.
- The requirements are divided into two sections:
  - **Mandatory Section**: You must complete ALL mandatory requirements to qualify.
  - **Bonus Section**: Attempt the bonus requirements only after completing the mandatory section. Bonus features will earn you extra points and provide an edge over other candidates.

## Problem Statement: LinkedIn Insights Microservice

Your task is to design and implement a LinkedIn Insights service, which is basically an application to check insights of a given Page ID of a LinkedIn Page, where Page ID means the last part we see in the Page's URL. For example: Boat company's page's URL is -> https://www.linkedin.com/company/deepsolv/, so `deepsolv` is the Page ID you'll get.

Your Application will be able to fetch details of a given Page ID (either by scraping or using API, we recommend scraping to save your development time, if not familiar with LinkedIn's APIs), store the required information into a Database, with separate schemas for Page, SocialMediaUser, Posts, etc. And we, as the operator of the application, can get the details of any LinkedIn Page, from the DB.

---

## MANDATORY Requirements

1. **Have a Scraper service** in your application, that scrapes any given Page ID from LinkedIn (you can use any existing scraping libraries available), for the following details of a Page. For example:
   - **Basic details of the Page**
     - Page Name
     - Page URL
     - id (the LinkedIn platform specific id)
     - Page Profile Picture
     - Description
     - Website
     - Page Industry
     - Total Followers
     - Head Count
     - Specialities
     - Any other fields you find useful or a good-to-have
   - **Posts of the Page** (you can have top few like 15-25 posts stored since, some pages might have a large number of posts)
   - **Comments on the Posts**
   - **People working there**, stored in DB

2. **Storing** the Scraped data into any DB, with relationships maintained between entities.

3. **Expose a GET endpoint** to get details of a given Page ID from the db (if a page is not present in the DB, then only try fetching it in realtime via scraping/API), with some filters like:
   - Find by follower count range, for eg. Find the pages between 20k-40k Followers
   - Find by name of the page (similar search)
   - Find by industry
   - Get list of the following/followers of a given Page
   - Get recent 10-15 Posts of the Page

4. **Have Pagination** in GET requests, wherever applicable.

5. **Make Sure** to create a Postman Collection of the included APIs, that you can directly share or present.

---

## BONUS Requirements

1. Provide **AI Summary** on a Page (using ChatGPT API, or any other LLMs) from the followers, like counts, type of page, about the page, type of followers.
2. Use **Asynchronous programming** for API calls, database operations, and any I/O-bound tasks.
3. Use a **Storage Server** like GCS, S3 etc. for the profile pictures or the Posts you're fetching, to make a clone of them in the server, and use that link as a mainstream link.
4. Implement **Caching** for the data, with TTL of for eg. 5 minutes for us to test.
5. Build a **Docker image** for the application.

---

## Deliverables

- A public GitHub repository Link.
- Documentation attached as README.md in the repo for easy understanding of your code.
- Postman Collection JSON (Optional)
- Deployed server link (Optional)
- Demo Video (optional)

## Submission

Submit your assignment on the Google Form - https://forms.gle/ei2pEYnbCPkgF35n8
