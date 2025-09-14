from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class DifficultyLevel(models.Model):
    level = models.IntegerField(
        unique=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    name = models.CharField(max_length=50, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.name:
            level_names = {
                1: "Beginner",
                2: "Elementary", 
                3: "Intermediate",
                4: "Advanced",
                5: "Expert"
            }
            self.name = level_names.get(self.level, f"Level {self.level}")
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Level {self.level}: {self.name}"

class Term(models.Model):
    title = models.CharField(max_length=200)
    explanation = models.TextField()
    difficulty = models.ForeignKey(DifficultyLevel, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.title

class RuleTheory(models.Model):
    title = models.CharField(max_length=200)
    explanation = models.TextField()
    difficulty = models.ForeignKey(DifficultyLevel, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.title

class Problem(models.Model):
    question = models.TextField()
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_answer = models.CharField(max_length=1, choices=[
        ('A', 'Option A'),
        ('B', 'Option B'),
        ('C', 'Option C'),
        ('D', 'Option D'),
    ])
    explanation = models.TextField()
    difficulty = models.ForeignKey(DifficultyLevel, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.question[:50] + "..." if len(self.question) > 50 else self.question

class TestQuestion(models.Model):
    question = models.TextField()
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_answer = models.CharField(max_length=1, choices=[
        ('A', 'Option A'),
        ('B', 'Option B'),
        ('C', 'Option C'),
        ('D', 'Option D'),
    ])
    explanation = models.TextField()
    difficulty = models.ForeignKey(DifficultyLevel, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.question[:50] + "..." if len(self.question) > 50 else self.question

class UserProgress(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    current_level = models.ForeignKey(DifficultyLevel, on_delete=models.CASCADE)
    terms_studied = models.ManyToManyField(Term, blank=True)
    rules_studied = models.ManyToManyField(RuleTheory, blank=True)
    problems_solved = models.ManyToManyField(Problem, blank=True)
    placement_test_taken = models.BooleanField(default=False)
    placement_test_score = models.FloatField(default=0)
    
    def __str__(self):
        return f"{self.user.username}'s Progress"
    
    def get_progress_percentage(self):
        """Calculate overall progress through all levels"""
        total_possible = 100  # This could be more sophisticated
        items_completed = (
            self.terms_studied.count() + 
            self.rules_studied.count() + 
            self.problems_solved.count()
        )
        return min((items_completed / total_possible * 100), 100) if total_possible > 0 else 0