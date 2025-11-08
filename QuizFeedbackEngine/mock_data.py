from models import Quiz, Question, Answer


MOCK_QUIZ = Quiz(
    title="Collisions and Momentum",
    questions=[
        Question(
            id=1,
            question_text="Which physical quantity is always conserved in a collision, regardless of the type?",
            answers=[
                Answer(text="Kinetic energy", is_correct=False),
                Answer(text="Momentum", is_correct=True),
                Answer(text="Resultant force", is_correct=False),
                Answer(text="Total mass", is_correct=False),
            ],
            user_answer_index=1
        ),
        Question(
            id=2,
            question_text="What condition defines a perfectly elastic collision?",
            answers=[
                Answer(text="Only momentum is conserved", is_correct=False),
                Answer(text="The bodies stick together", is_correct=False),
                Answer(text="Momentum and kinetic energy are conserved", is_correct=True),
                Answer(text="Potential energy decreases", is_correct=False),
            ],
            user_answer_index=2
        ),
        Question(
            id=3,
            question_text="In an inelastic collision, part of the initial kinetic energy is transformed into:",
            answers=[
                Answer(text="Light", is_correct=False),
                Answer(text="Heat and deformations", is_correct=True),
                Answer(text="Gravitational potential energy", is_correct=False),
                Answer(text="Additional mass", is_correct=False),
            ],
            user_answer_index=0
        ),
        Question(
            id=4,
            question_text="If a light ball collides with a heavy stationary ball, what typically happens?",
            answers=[
                Answer(text="Both stop", is_correct=False),
                Answer(text="The light ball bounces back", is_correct=True),
                Answer(text="The heavy ball accelerates strongly", is_correct=False),
                Answer(text="They move together with the same speed", is_correct=False),
            ],
            user_answer_index=1
        ),
        Question(
            id=5,
            question_text="The coefficient of restitution expresses:",
            answers=[
                Answer(text="Loss of mass", is_correct=False),
                Answer(text="The ratio of velocities after and before the collision", is_correct=True),
                Answer(text="The ratio of momenta", is_correct=False),
                Answer(text="The change in potential energy", is_correct=False),
            ],
            user_answer_index=1
        ),
        Question(
            id=6,
            question_text="For e = 0, what type of collision do we have?",
            answers=[
                Answer(text="Perfectly elastic collision", is_correct=False),
                Answer(text="Perfectly inelastic collision", is_correct=True),
                Answer(text="Partially elastic collision", is_correct=False),
                Answer(text="Superelastic collision", is_correct=False),
            ],
            user_answer_index=0
        ),
        Question(
            id=7,
            question_text="Which of the following is a vector quantity?",
            answers=[
                Answer(text="Kinetic energy", is_correct=False),
                Answer(text="Momentum", is_correct=True),
                Answer(text="Temperature", is_correct=False),
                Answer(text="Speed", is_correct=False),
            ],
            user_answer_index=1
        ),
        Question(
            id=8,
            question_text="In a 2D collision, why must the conservation law be applied on each axis?",
            answers=[
                Answer(text="Because momentum is a scalar", is_correct=False),
                Answer(text="Because energy components are independent", is_correct=False),
                Answer(text="Because momentum is a vector and components along axes are independent", is_correct=True),
                Answer(text="Because forces act only along coordinate axes", is_correct=False),
            ],
            user_answer_index=2
        ),
        Question(
            id=9,
            question_text="In an elastic collision with equal masses, if one is at rest and e = 1, what happens?",
            answers=[
                Answer(text="Both stop", is_correct=False),
                Answer(text="The initial ball stops and the other takes the entire velocity", is_correct=True),
                Answer(text="They stick together", is_correct=False),
                Answer(text="Both rebound with half the initial speed", is_correct=False),
            ],
            user_answer_index=1
        ),
        Question(
            id=10,
            question_text="What happens to the total energy if e < 1?",
            answers=[
                Answer(text="Kinetic energy increases; momentum is conserved", is_correct=False),
                Answer(text="Kinetic energy decreases; momentum is conserved", is_correct=True),
                Answer(text="Both kinetic energy and momentum increase", is_correct=False),
                Answer(text="Momentum is lost", is_correct=False),
            ],
            user_answer_index=3
        ),
    ]
)


MOCK_QUIZ_2 = MOCK_QUIZ
