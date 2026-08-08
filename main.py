from core.engine import BearCore


def main():
    bearcore = BearCore()

    print("==============================")
    print("        BearCore V2")
    print("==============================")
    print("Komennot:")
    print("  muisti   - Näytä muistissa olevat viestit")
    print("  historia - Näytä keskusteluhistoria")
    print("  exit     - Sulje BearCore")
    print()

    while True:
        message = input("Sinä: ").strip()

        if message.lower() == "exit":
            print("BearCore: Suljetaan...")
            break

        if message.lower() == "muisti":
            memories = bearcore.memory.get_memories()

            if memories:
                print("\nBearCore muistaa:")
                for memory in memories:
                    print(f"- {memory}")
            else:
                print("\nBearCore: Muisti on tyhjä.")

            print()
            continue

        if message.lower() == "historia":
            history = bearcore.conversation.get_history()

            if history:
                print("\nKeskusteluhistoria:")
                for item in history:
                    print(f"{item['role']}: {item['content']}")
            else:
                print("\nBearCore: Keskusteluhistoria on tyhjä.")

            print()
            continue

        response = bearcore.process(message)
        print(f"BearCore: {response}")


if __name__ == "__main__":
    main()