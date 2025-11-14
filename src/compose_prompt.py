# src/compose_prompt.py
def build_mureka_payload(mnemonic_plan, study_text):
    """
    Build a request payload for Mureka's song generation endpoint.
    Reference: https://platform.mureka.ai/docs/en/quickstart.html
    """
    prompt = (
        "bright educational jingle, clear Korean diction, playful synth pop,"
        " memorable hook, repetition for easy memorisation"
    )
    return {
        "lyrics": f"{study_text}\n\n[Mnemonic Guide]\n{mnemonic_plan}",
        "model": "auto",
        "prompt": prompt,
    }