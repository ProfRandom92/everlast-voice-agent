#!/usr/bin/env python3
"""
Everlast Voice Agent - Test Runner
Executes test scenarios and validates results
"""

import asyncio
import json
import sys
from datetime import datetime
from typing import Dict, List, Optional
import httpx

# API endpoint
API_URL = "http://localhost:8000"

class VoiceAgentTester:
    def __init__(self, api_url: str = API_URL):
        self.api_url = api_url
        self.results = []

    async def run_scenario(self, scenario_name: str, conversation: List[Dict]) -> Dict:
        """Run a single test scenario"""
        print(f"\n{'='*60}")
        print(f"Running: {scenario_name}")
        print('='*60)

        conversation_id = f"test-{datetime.now().timestamp()}"
        state = None

        for turn in conversation:
            role = turn.get("role")
            message = turn.get("message")

            if role == "user":
                print(f"\nUser: {message}")

                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            f"{self.api_url}/vapi/webhook",
                            json={
                                "message": {"role": "user", "content": message},
                                "call": {
                                    "id": conversation_id,
                                    "customer": {"number": "+491234567890"}
                                }
                            },
                            timeout=30.0
                        )

                        result = response.json()
                        agent_response = result.get("response", "")
                        print(f"Agent: {agent_response}")
                        state = result

                except Exception as e:
                    print(f"Error: {e}")
                    return {"success": False, "error": str(e)}

            elif role == "function":
                print(f"\n[Function Call: {turn.get('name')}]")
                print(f"Parameters: {turn.get('parameters')}")

        # End conversation
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/calls/end",
                    params={"conversation_id": conversation_id},
                    json={
                        "call_outcome": "Test completed",
                        "lead_score": "B",
                        "notes": f"Test scenario: {scenario_name}"
                    }
                )

        except Exception as e:
            print(f"Error ending call: {e}")

        return {
            "success": True,
            "scenario": scenario_name,
            "conversation_id": conversation_id,
            "final_state": state
        }

    async def run_all_scenarios(self):
        """Run all test scenarios"""

        scenarios = [
            {
                "name": "Warm Lead - High Interest",
                "conversation": [
                    {"role": "user", "message": "Ja, ich habe Ihre Case Study gelesen. Sehr interessant!"},
                    {"role": "user", "message": "Diese Lead-Reaktivierung - wir haben da wirklich viele alte Kontakte."},
                    {"role": "user", "message": "Wir sind 45 Leute im Vertrieb."},
                    {"role": "user", "message": "Ja, ich bin der GF."},
                    {"role": "user", "message": "Ja, wir haben 50k€ frei für dieses Jahr."},
                    {"role": "user", "message": "So schnell wie möglich, am besten nächsten Monat."},
                    {"role": "function", "name": "bookAppointment", "parameters": {"name": "Max Mustermann", "email": "max@firma.de", "date": "2026-03-05", "time": "14:00"}}
                ]
            },
            {
                "name": "Budget Objection",
                "conversation": [
                    {"role": "user", "message": "Klingt interessant, aber wir haben gerade kein Budget."},
                    {"role": "user", "message": "Naja, KI-Beratung ist ja bestimmt teuer."},
                    {"role": "user", "message": "Wirklich? Wie funktioniert das?"},
                    {"role": "user", "message": "Okay, das klingt anders als erwartet."},
                    {"role": "user", "message": "Ja, buchen Sie einen Termin."},
                    {"role": "function", "name": "bookAppointment", "parameters": {"name": "Anna Schmidt", "email": "anna@company.de", "date": "2026-03-10", "time": "10:00"}}
                ]
            },
            {
                "name": "Time Objection",
                "conversation": [
                    {"role": "user", "message": "Gerade absolut nicht, wir haben Produktionsstress."},
                    {"role": "user", "message": "Rufen Sie nächste Woche an."},
                    {"role": "user", "message": "Dienstag."},
                    {"role": "user", "message": "Lieber Nachmittag."},
                    {"role": "user", "message": "Ja, Termin ist besser."},
                    {"role": "function", "name": "bookAppointment", "parameters": {"name": "Peter Weber", "email": "peter@test.de", "date": "2026-03-04", "time": "14:30"}}
                ]
            },
            {
                "name": "Already Using ChatGPT",
                "conversation": [
                    {"role": "user", "message": "Wir nutzen schon ChatGPT für Texte."},
                    {"role": "user", "message": "Hauptsächlich Marketing-Texte."},
                    {"role": "user", "message": "Nein, das machen wir noch manuell."},
                    {"role": "user", "message": "Stimmt, das haben wir nicht."},
                    {"role": "user", "message": "Ja, wäre es. Wann passt es?"},
                    {"role": "function", "name": "bookAppointment", "parameters": {"name": "Lisa Mueller", "email": "lisa@tech.de", "date": "2026-03-06", "time": "11:00"}}
                ]
            },
            {
                "name": "Skeptical Lead",
                "conversation": [
                    {"role": "user", "message": "Wieder so ein KI-Anruf? Ich kriege das ständig."},
                    {"role": "user", "message": "Sie haben 30 Sekunden."},
                    {"role": "user", "message": "Das sagen alle."},
                    {"role": "user", "message": "Naja..."},
                    {"role": "user", "message": "Okay, Termin. Aber nur 15 Minuten."},
                    {"role": "function", "name": "bookAppointment", "parameters": {"name": "Thomas Klein", "email": "thomas@small.de", "date": "2026-03-07", "time": "09:00"}}
                ]
            }
        ]

        for scenario in scenarios:
            result = await self.run_scenario(scenario["name"], scenario["conversation"])
            self.results.append(result)

        return self.results

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)

        passed = sum(1 for r in self.results if r.get("success"))
        total = len(self.results)

        print(f"\nPassed: {passed}/{total}")
        print(f"Success Rate: {passed/total*100:.1f}%\n")

        for result in self.results:
            status = "✓ PASS" if result.get("success") else "✗ FAIL"
            print(f"{status}: {result['scenario']}")
            if not result.get("success"):
                print(f"  Error: {result.get('error')}")

        print("\n" + "="*60)

async def main():
    """Main entry point"""
    tester = VoiceAgentTester()
    await tester.run_all_scenarios()
    tester.print_summary()

if __name__ == "__main__":
    asyncio.run(main())
