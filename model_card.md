# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

Model Name: CLaudeVibeMaster

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

This reccomender basically suggests songs from a very small cataloguebased on a user's stated genre, or mood, or energy prefrerence. It is built for classroom exploration only and is not intended for real users or production use.

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

    Every song in the catalog is given a score based on how well it matches the user's favorite genre, favorite mood, and target energy level closer matches earn more points. The song with the highest total score ranks first, and each result comes with a plain-English explanation of exactly why it was chosen

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

    The catalog contains 18 songs spanning 15 genres including lofi, pop, rock, jazz, EDM, metal, country, and soul, with 10 mood labels. Eight songs were added to the original starter dataset to improve genre and mood diversity.

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

    The system works best when a user has a clear, specific taste for example a lofi/chill listener gets two near-perfect matches at the top every time. Every recommendation also comes with visible reasons, making it easy to understand and trust the output.

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

    The likes_acoustic preference is collected from the user but never used in scoring, so acoustic taste is completely ignored. Most genres have only one song in the catalog, meaning 13 out of 15 genre groups get one strong match and then four nearly-random results.

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

    Six user profiles were tested including three adversarial edge cases a conflicting energy/mood profile, a rare genre, and a dead-center energy profile. The biggest surprise was that the rare-genre user scored 4.00 at position one and below 1.00 at every other position, revealing how much catalog size affects result quality.


---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

    The most important next step is wiring likes_acoustic into the scoring formula so that preference actually influences results. Adding more songs per genre and introducing a mood-cluster system (so "chill" and "relaxed" are treated as related) would make the recommendations feel much more natural.

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  

    Working on this project and building this music reccomender with ai-assistanse helped me realized that typical reccomenders are only as good as the data it has on you. The algorithm that was created was pretty accurate but the thin catalogue of songs and data made the results feel more shallow for most of the genre groups. it also changed how I think about Spotify recommendations: what feels like deep personalization is likely backed by millions of data points that smooth over the exact catalog-size problems this simulation exposed.