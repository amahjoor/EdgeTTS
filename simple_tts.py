#!/usr/bin/env python3
"""
Ultra-Simple TTS Program
Uses Microsoft Edge TTS voices from voices.txt
"""

import asyncio
import edge_tts
import os
import sys
import re
from pathlib import Path

class SimpleTTS:
    def __init__(self):
        self.voices = []
        self.load_voices()
    
    def load_voices(self):
        """Parse voices.txt and extract voice information"""
        try:
            with open('voices.txt', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split by voice entries (each starts with "Name:")
            voice_blocks = content.split('Name: Microsoft Server Speech Text to Speech Voice')[1:]
            
            for block in voice_blocks:
                lines = block.strip().split('\n')
                if len(lines) >= 4:
                    try:
                        # Extract voice info
                        name_line = lines[0].strip()
                        short_name = lines[1].replace('ShortName: ', '').strip()
                        gender = lines[2].replace('Gender: ', '').strip()
                        locale = lines[3].replace('Locale: ', '').strip()
                        
                        # Extract language code (first part before hyphen)
                        lang_code = locale.split('-')[0] if '-' in locale else locale
                        
                        voice_info = {
                            'name': f"Microsoft Edge TTS {name_line}",
                            'short_name': short_name,
                            'gender': gender,
                            'locale': locale,
                            'language': lang_code
                        }
                        self.voices.append(voice_info)
                    except Exception as e:
                        continue
                        
            print(f"✅ Loaded {len(self.voices)} voices from voices.txt")
            
        except FileNotFoundError:
            print("❌ voices.txt not found!")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error loading voices: {e}")
            sys.exit(1)
    
    def search_voices(self, query=""):
        """Search voices by language, gender, or name"""
        if not query:
            return self.voices
        
        query = query.lower()
        results = []
        
        for voice in self.voices:
            if (query in voice['short_name'].lower() or 
                query in voice['language'].lower() or 
                query in voice['gender'].lower() or
                query in voice['locale'].lower()):
                results.append(voice)
        
        return results
    
    def display_voices(self, voices, limit=20):
        """Display voices in a formatted table"""
        if not voices:
            print("❌ No voices found")
            return
        
        print(f"\n📢 Found {len(voices)} voice(s):")
        print("-" * 80)
        print(f"{'#':<3} {'Short Name':<25} {'Language':<8} {'Gender':<8} {'Locale':<12}")
        print("-" * 80)
        
        for i, voice in enumerate(voices[:limit], 1):
            print(f"{i:<3} {voice['short_name']:<25} {voice['language']:<8} {voice['gender']:<8} {voice['locale']:<12}")
        
        if len(voices) > limit:
            print(f"... and {len(voices) - limit} more voices")
        print("-" * 80)
    
    def get_voice_by_number(self, voices, number):
        """Get voice by number from displayed list"""
        try:
            index = int(number) - 1
            if 0 <= index < len(voices):
                return voices[index]
        except ValueError:
            pass
        return None
    
    def get_voice_by_name(self, short_name):
        """Get voice by exact short name"""
        for voice in self.voices:
            if voice['short_name'].lower() == short_name.lower():
                return voice
        return None
    
    async def speak(self, text, voice_name, output_file=None):
        """Convert text to speech using selected voice"""
        try:
            print(f"🎤 Generating speech with voice: {voice_name}")
            
            # Create TTS object
            tts = edge_tts.Communicate(text, voice_name)
            
            if output_file:
                # Save to file
                await tts.save(output_file)
                print(f"💾 Audio saved to: {output_file}")
            else:
                # Save to temporary file and play
                temp_file = "temp_tts_output.mp3"
                await tts.save(temp_file)
                print(f"🎵 Playing audio...")
                
                # Try to play the audio
                if sys.platform.startswith('darwin'):  # macOS
                    os.system(f'afplay "{temp_file}"')
                elif sys.platform.startswith('win'):   # Windows
                    os.system(f'start "" "{temp_file}"')
                else:  # Linux
                    os.system(f'mpg123 "{temp_file}" 2>/dev/null || aplay "{temp_file}" 2>/dev/null')
                
                # Clean up temp file
                try:
                    os.remove(temp_file)
                except:
                    pass
                    
        except Exception as e:
            print(f"❌ Error generating speech: {e}")
    
    async def interactive_mode(self):
        """Run interactive TTS session"""
        print("\n🎙️  Welcome to Ultra-Simple TTS!")
        print("Commands:")
        print("  'list' or 'l' - Show all voices")
        print("  'search <query>' or 's <query>' - Search voices")
        print("  'speak <text>' - Use last selected voice")
        print("  'bulk <number>' - Test multiple voices (e.g., 'bulk 10')")
        print("  'bulk all' - Test ALL voices (302 voices - may take a while!)")
        print("  'quit' or 'q' - Exit")
        print("  Just type a number to select a voice from the list")
        
        current_voice = None
        last_search_results = self.voices[:20]  # Show first 20 by default
        
        self.display_voices(last_search_results)
        
        while True:
            try:
                user_input = input("\n🎯 Enter command: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'q', 'exit']:
                    print("👋 Goodbye!")
                    break
                
                elif user_input.lower() in ['list', 'l']:
                    last_search_results = self.voices
                    self.display_voices(last_search_results)
                
                elif user_input.lower().startswith('search ') or user_input.lower().startswith('s '):
                    query = user_input.split(' ', 1)[1] if len(user_input.split(' ', 1)) > 1 else ""
                    last_search_results = self.search_voices(query)
                    self.display_voices(last_search_results)
                
                elif user_input.lower().startswith('speak '):
                    if current_voice:
                        text = user_input[6:].strip()
                        if text:
                            await self.speak(text, current_voice['short_name'])
                        else:
                            print("❌ Please provide text to speak")
                    else:
                        print("❌ Please select a voice first")
                
                elif user_input.lower().startswith('bulk '):
                    bulk_param = user_input[5:].strip().lower()
                    if bulk_param == 'all':
                        confirm = input("⚠️  This will test ALL 302 voices! Continue? (y/N): ").strip().lower()
                        if confirm == 'y':
                            await self.bulk_test_voices()
                    else:
                        try:
                            num_voices = int(bulk_param)
                            if num_voices > 0:
                                await self.bulk_test_voices(max_voices=num_voices)
                            else:
                                print("❌ Please provide a positive number")
                        except ValueError:
                            print("❌ Invalid number. Use 'bulk 10' or 'bulk all'")
                
                elif user_input.isdigit():
                    # Select voice by number
                    selected_voice = self.get_voice_by_number(last_search_results, user_input)
                    if selected_voice:
                        current_voice = selected_voice
                        print(f"✅ Selected voice: {current_voice['short_name']} ({current_voice['gender']}, {current_voice['locale']})")
                        
                        # Ask for text to speak
                        text = input("💬 Enter text to speak (or press Enter to skip): ").strip()
                        if text:
                            await self.speak(text, current_voice['short_name'])
                    else:
                        print("❌ Invalid voice number")
                
                else:
                    # Try to find voice by name or treat as text to speak
                    voice = self.get_voice_by_name(user_input)
                    if voice:
                        current_voice = voice
                        print(f"✅ Selected voice: {current_voice['short_name']}")
                    elif current_voice:
                        # Treat as text to speak
                        await self.speak(user_input, current_voice['short_name'])
                    else:
                        print("❌ Unknown command. Type 'list' to see voices or select a voice first.")
                        
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    async def bulk_test_voices(self, save_audio=False, max_voices=None):
        """Bulk test multiple voices - can be called from interactive mode"""
        voices_to_test = self.voices[:max_voices] if max_voices else self.voices
        
        print(f"🚀 Starting bulk test of {len(voices_to_test)} voices...")
        print("⚠️  This may take a while. Press Ctrl+C to stop.")
        
        success_count = 0
        failed_count = 0
        
        for i, voice in enumerate(voices_to_test, 1):
            try:
                # Get appropriate test text for the language
                lang_code = voice['locale'].split('-')[0].lower()
                test_texts = {
                    'en': "Hello, this is a test.",
                    'zh': "你好，这是测试。",
                    'es': "Hola, esta es una prueba.",
                    'fr': "Bonjour, c'est un test.",
                    'de': "Hallo, das ist ein Test.",
                    'ja': "こんにちは、これはテストです。",
                    'ko': "안녕하세요, 테스트입니다."
                }
                test_text = test_texts.get(lang_code, "Hello, this is a test.")
                
                print(f"🎤 [{i}/{len(voices_to_test)}] Testing {voice['short_name']} ({voice['locale']})")
                
                if save_audio:
                    filename = f"bulk_test_{voice['short_name']}.mp3"
                    await self.speak(test_text, voice['short_name'], filename)
                else:
                    await self.speak(test_text, voice['short_name'])
                
                success_count += 1
                print(f"✅ Success")
                
            except KeyboardInterrupt:
                print("\n🛑 Bulk test interrupted by user")
                break
            except Exception as e:
                failed_count += 1
                print(f"❌ Failed: {e}")
        
        # Show summary
        total_tested = success_count + failed_count
        success_rate = (success_count / total_tested * 100) if total_tested > 0 else 0
        
        print(f"\n📊 BULK TEST SUMMARY:")
        print(f"   Total tested: {total_tested}")
        print(f"   Successful: {success_count}")
        print(f"   Failed: {failed_count}")
        print(f"   Success rate: {success_rate:.1f}%")

async def main():
    """Main function"""
    tts = SimpleTTS()
    
    # Check command line arguments
    if len(sys.argv) == 1:
        # Interactive mode
        await tts.interactive_mode()
    
    elif len(sys.argv) >= 3:
        # Command line mode: python simple_tts.py "voice_name" "text to speak" [output_file]
        voice_name = sys.argv[1]
        text = sys.argv[2]
        output_file = sys.argv[3] if len(sys.argv) > 3 else None
        
        # Find voice
        voice = tts.get_voice_by_name(voice_name)
        if voice:
            await tts.speak(text, voice['short_name'], output_file)
        else:
            print(f"❌ Voice '{voice_name}' not found")
            print("Available voices:")
            results = tts.search_voices(voice_name)
            tts.display_voices(results, 10)
    
    else:
        print("Usage:")
        print("  python simple_tts.py                              # Interactive mode")
        print("  python simple_tts.py 'voice_name' 'text'          # Direct TTS")
        print("  python simple_tts.py 'voice_name' 'text' 'output.mp3'  # Save to file")

if __name__ == "__main__":
    asyncio.run(main()) 