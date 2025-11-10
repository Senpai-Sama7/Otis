"""
Red Team Attack Vectors Example

This example demonstrates various adversarial attack techniques against
the anti-spam model, simulating how attackers might try to fool the system.
"""

from src.adversarial.attack_vectors import (
    CharacterObfuscationAttack,
    EncodingEvasionAttack,
    HomographSubstitutionAttack,
    MultilingualInjectionAttack,
    PromptInjectionAttack,
    SemanticShiftAttack,
)


def demonstrate_attack_vectors():
    """Demonstrate all six attack vectors."""
    print("=== Red Team Attack Vectors Demonstration ===\n")

    # Base spam message to attack
    base_message = "Get rich quick! Click here now for amazing offers!"
    print(f"Original message: {base_message}\n")

    # 1. Character Obfuscation Attack
    print("1. Character Obfuscation Attack:")
    obfuscation_attack = CharacterObfuscationAttack()
    obfuscated_result = obfuscation_attack.execute(base_message)
    print(f"   Original: {base_message}")
    print(f"   Modified: {obfuscated_result.modified_text}")
    print(f"   Characters changed: {obfuscated_result.metadata['chars_modified']}")
    print(f"   Success: {obfuscated_result.success}\n")

    # 2. Semantic Shift Attack
    print("2. Semantic Shift Attack:")
    semantic_attack = SemanticShiftAttack()
    semantic_result = semantic_attack.execute(base_message)
    print(f"   Original: {base_message}")
    print(f"   Modified: {semantic_result.modified_text}")
    print(f"   Words changed: {semantic_result.metadata['words_modified']}")
    print(f"   Success: {semantic_result.success}\n")

    # 3. Prompt Injection Attack
    print("3. Prompt Injection Attack:")
    injection_attack = PromptInjectionAttack()
    injection_result = injection_attack.execute(base_message)
    print(f"   Original: {base_message}")
    print(f"   Modified: {injection_result.modified_text}")
    print(f"   Injection applied: {injection_result.metadata.get('injection_applied', 'N/A')}")
    print(f"   Success: {injection_result.success}\n")

    # 4. Multilingual Injection Attack
    print("4. Multilingual Injection Attack:")
    multilingual_attack = MultilingualInjectionAttack()
    multilingual_result = multilingual_attack.execute(base_message)
    print(f"   Original: {base_message}")
    print(f"   Modified: {multilingual_result.modified_text}")
    print(f"   Language injected: {multilingual_result.metadata.get('injected_language', 'N/A')}")
    print(f"   Success: {multilingual_result.success}\n")

    # 5. Encoding Evasion Attack
    print("5. Encoding Evasion Attack:")
    encoding_attack = EncodingEvasionAttack()
    encoding_result = encoding_attack.execute(base_message)
    print(f"   Original: {base_message}")
    print(f"   Modified: {encoding_result.modified_text}")
    print(f"   Chars encoded: {encoding_result.metadata['chars_encoded']}")
    print(f"   Success: {encoding_result.success}\n")

    # 6. Homograph Substitution Attack
    print("6. Homograph Substitution Attack:")
    homograph_attack = HomographSubstitutionAttack()
    homograph_result = homograph_attack.execute(base_message)
    print(f"   Original: {base_message}")
    print(f"   Modified: {homograph_result.modified_text}")
    print(f"   Chars substituted: {homograph_result.metadata['chars_substituted']}")
    print(f"   Success: {homograph_result.success}\n")


def attack_effectiveness_comparison():
    """Compare the effectiveness of different attacks."""
    print("=== Attack Effectiveness Comparison ===\n")

    base_messages = [
        "Free money opportunity",
        "Win amazing prizes now",
        "Urgent account verification"
    ]

    attacks = {
        "Obfuscation": CharacterObfuscationAttack(),
        "Semantic": SemanticShiftAttack(),
        "Injection": PromptInjectionAttack(),
        "Encoding": EncodingEvasionAttack(),
        "Homograph": HomographSubstitutionAttack()
    }

    print("Effectiveness across different message types:\n")

    for msg in base_messages:
        print(f"Message: '{msg}'")
        for name, attack in attacks.items():
            try:
                result = attack.execute(msg)
                print(f"  {name:12}: {result.metadata.get('chars_modified', result.metadata.get('words_modified', result.metadata.get('chars_encoded', result.metadata.get('chars_substituted', 0))))} changes")
            except Exception as e:
                print(f"  {name:12}: Error - {str(e)[:30]}...")
        print()


if __name__ == "__main__":
    demonstrate_attack_vectors()
    print("\n" + "="*60 + "\n")
    attack_effectiveness_comparison()
