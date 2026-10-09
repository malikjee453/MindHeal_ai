from core.safety import assess_safety
def test_safety(): assert assess_safety("I am having a difficult day.").level in {"low","moderate","high","crisis"}
