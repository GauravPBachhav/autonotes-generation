"""Quick integration test – validates each section is DIFFERENT"""
import sys
sys.path.insert(0, "backend")

from modules.processor import TextProcessor
from modules.summarizer import Summarizer

print("=" * 70)
print("  TEST: Unpunctuated speech-recognition transcript")
print("=" * 70)

# ── This mimics REAL speech-to-text output: NO punctuation at all ──
raw_speech = (
    "what is the static keyword in Java the static keyword in Java is used "
    "for memory management it can be applied to variables methods blocks and "
    "nested classes the static variable is shared among all instances of a class "
    "when we declare a variable as static only a single copy is created and shared "
    "among all objects the static method belongs to the class rather than object of "
    "the class it can be invoked without creating an instance of the class the "
    "static block is used to initialize static variables it is executed before the "
    "main method at the time of class loading static nested class can access only "
    "the static members of the outer class the advantage of static keyword is "
    "memory efficiency because static members are stored only once in class area"
)

print(f"\n📄 Raw input: {len(raw_speech.split())} words, NO punctuation\n")

# ── 1. Processor ──
p = TextProcessor()
result = p.process_transcript(raw_speech)

print("─── After processing ───")
print(f"  Sentences detected : {result['sentence_count']}")
print(f"  Topics detected    : {result['section_count']}")
print(f"  Keywords           : {', '.join(result['keywords'][:6])}")

notes = result["structured_notes"]

print("\n─── TOPIC-WISE NOTES (short bullets) ───")
for i, t in enumerate(notes["topics"]):
    print(f"\n  📌 Topic {i+1}: {t['title']}")
    for b in t["bullet_points"]:
        print(f"     • {b}")

print("\n─── KEY TAKEAWAYS (labelled/categorised) ───")
for ta in notes["key_takeaways"]:
    print(f"  ✅ {ta}")

print("\n─── QUICK REVISION ───")
for qr in notes["quick_revision"]:
    print(f"  ⚡ {qr}")

print("\n─── DEFINITIONS ───")
for d in notes["definitions"]:
    print(f"  📖 {d['term']}: {d['definition'][:80]}")

# ── 2. Summarizer ──
s = Summarizer()
summary = s.summarize(result["cleaned_text"])
bullets = s.extract_bullet_points(result["cleaned_text"], num_points=5)

print(f"\n─── SUMMARY ({len(summary.split())} words) ───")
print(f"  {summary}")

print(f"\n─── IMPORTANT POINTS ({len(bullets)}) ───")
for bp in bullets:
    print(f"  📍 {bp}")

# ── 3. Verify DIFFERENTIATION ──
print("\n" + "=" * 70)
print("  DIFFERENTIATION CHECK")
print("=" * 70)

topic_bullets = [b for t in notes["topics"] for b in t["bullet_points"]]
takeaways = notes["key_takeaways"]
imp_points = bullets

# They should NOT be identical
all_same = (set(topic_bullets) == set(takeaways) == set(imp_points))
if all_same and len(topic_bullets) > 0:
    print("  ❌ FAIL: All sections contain identical content!")
else:
    print("  ✅ PASS: Sections contain genuinely different content")
    print(f"     Topic bullets  : {len(topic_bullets)} items")
    print(f"     Key takeaways  : {len(takeaways)} items")
    print(f"     Important pts  : {len(imp_points)} items")

# Check summary is shorter than original
orig_words = len(raw_speech.split())
sum_words = len(summary.split())
if sum_words < orig_words:
    print(f"  ✅ PASS: Summary is compressed ({orig_words} → {sum_words} words)")
else:
    print(f"  ❌ FAIL: Summary not compressed ({orig_words} → {sum_words} words)")

print("\n✅ All tests finished.")
