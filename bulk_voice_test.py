#!/usr/bin/env python3
"""
Bulk Voice Test Script
Tests every single voice from voices.txt automatically
"""

import asyncio
import os
import time
from pathlib import Path
from simple_tts import SimpleTTS

class BulkVoiceTester:
    def __init__(self):
        self.tts = SimpleTTS()
        self.test_text = "Hello, this is a test of the text to speech system. The quick brown fox jumps over the lazy dog."
        self.results = {
            'success': [],
            'failed': [],
            'total': 0,
            'start_time': None,
            'end_time': None
        }
        
    def get_test_text_for_language(self, locale):
        """Get appropriate test text based on language"""
        lang_code = locale.split('-')[0].lower()
        
        test_texts = {
            'en': "Hello, this is a test of the text to speech system.",
            'zh': "你好，这是语音合成系统的测试。",
            'es': "Hola, esta es una prueba del sistema de síntesis de voz.",
            'fr': "Bonjour, ceci est un test du système de synthèse vocale.",
            'de': "Hallo, dies ist ein Test des Sprachsynthese-Systems.",
            'ja': "こんにちは、これは音声合成システムのテストです。",
            'ko': "안녕하세요, 이것은 음성 합성 시스템의 테스트입니다.",
            'it': "Ciao, questo è un test del sistema di sintesi vocale.",
            'pt': "Olá, este é um teste do sistema de síntese de voz.",
            'ru': "Привет, это тест системы синтеза речи.",
            'ar': "مرحبا، هذا اختبار لنظام تحويل النص إلى كلام.",
            'hi': "नमस्ते, यह टेक्स्ट टू स्पीच सिस्टम का परीक्षण है।",
            'th': "สวัสดี นี่คือการทดสอบระบบแปลงข้อความเป็นเสียงพูด",
            'vi': "Xin chào, đây là thử nghiệm hệ thống chuyển văn bản thành giọng nói.",
            'tr': "Merhaba, bu metin okuma sisteminin bir testidir.",
            'nl': "Hallo, dit is een test van het tekst-naar-spraak systeem.",
            'sv': "Hej, det här är ett test av text-till-tal-systemet.",
            'da': "Hej, dette er en test af tekst-til-tale systemet.",
            'no': "Hei, dette er en test av tekst-til-tale-systemet.",
            'fi': "Hei, tämä on teksti puheeksi -järjestelmän testi.",
            'pl': "Cześć, to jest test systemu zamiany tekstu na mowę.",
            'cs': "Ahoj, toto je test systému převodu textu na řeč.",
            'hu': "Helló, ez a szövegfelolvasó rendszer tesztje.",
            'ro': "Salut, acesta este un test al sistemului text-to-speech."
        }
        
        return test_texts.get(lang_code, self.test_text)
    
    async def test_single_voice(self, voice, voice_number, total_voices, save_audio=False):
        """Test a single voice"""
        try:
            test_text = self.get_test_text_for_language(voice['locale'])
            
            print(f"🎤 [{voice_number}/{total_voices}] Testing {voice['short_name']} ({voice['gender']}, {voice['locale']})")
            
            if save_audio:
                # Create output directory if it doesn't exist
                output_dir = Path("voice_samples")
                output_dir.mkdir(exist_ok=True)
                
                # Create filename with voice info
                filename = f"{voice['short_name']}_{voice['gender']}_{voice['locale']}.mp3"
                output_file = output_dir / filename
                
                await self.tts.speak(test_text, voice['short_name'], str(output_file))
                
                # Verify file was created and has content
                if output_file.exists() and output_file.stat().st_size > 0:
                    self.results['success'].append({
                        'voice': voice,
                        'file': str(output_file),
                        'file_size': output_file.stat().st_size
                    })
                    print(f"✅ Success - {voice['short_name']} (File: {output_file.stat().st_size} bytes)")
                else:
                    raise Exception("Generated file is empty or missing")
            else:
                # Just test generation without saving
                temp_file = f"temp_test_{voice['short_name']}.mp3"
                await self.tts.speak(test_text, voice['short_name'], temp_file)
                
                # Check if file was created
                if os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
                    self.results['success'].append({
                        'voice': voice,
                        'file_size': os.path.getsize(temp_file)
                    })
                    print(f"✅ Success - {voice['short_name']} ({os.path.getsize(temp_file)} bytes)")
                    # Clean up temp file
                    os.remove(temp_file)
                else:
                    raise Exception("Generated file is empty or missing")
                    
        except Exception as e:
            self.results['failed'].append({
                'voice': voice,
                'error': str(e)
            })
            print(f"❌ Failed - {voice['short_name']}: {e}")
    
    async def test_all_voices(self, save_audio=False, max_concurrent=5):
        """Test all voices with concurrent processing"""
        print(f"🚀 Starting bulk voice test...")
        print(f"📊 Total voices to test: {len(self.tts.voices)}")
        print(f"🎯 Save audio files: {'Yes' if save_audio else 'No'}")
        print(f"⚡ Max concurrent tests: {max_concurrent}")
        print("-" * 80)
        
        self.results['total'] = len(self.tts.voices)
        self.results['start_time'] = time.time()
        
        # Create semaphore to limit concurrent operations
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def test_with_semaphore(voice, voice_number):
            async with semaphore:
                await self.test_single_voice(voice, voice_number, len(self.tts.voices), save_audio)
        
        # Create tasks for all voices
        tasks = []
        for i, voice in enumerate(self.tts.voices, 1):
            task = test_with_semaphore(voice, i)
            tasks.append(task)
        
        # Run all tests
        await asyncio.gather(*tasks, return_exceptions=True)
        
        self.results['end_time'] = time.time()
        
        # Show results
        self.show_results()
    
    async def test_by_language(self, language_code, save_audio=False):
        """Test all voices for a specific language"""
        matching_voices = [v for v in self.tts.voices if v['language'].lower() == language_code.lower()]
        
        if not matching_voices:
            print(f"❌ No voices found for language: {language_code}")
            return
        
        print(f"🎯 Testing {len(matching_voices)} voices for language: {language_code}")
        print("-" * 80)
        
        self.results['total'] = len(matching_voices)
        self.results['start_time'] = time.time()
        
        for i, voice in enumerate(matching_voices, 1):
            await self.test_single_voice(voice, i, len(matching_voices), save_audio)
        
        self.results['end_time'] = time.time()
        self.show_results()
    
    def show_results(self):
        """Display comprehensive test results"""
        duration = self.results['end_time'] - self.results['start_time']
        success_count = len(self.results['success'])
        failed_count = len(self.results['failed'])
        success_rate = (success_count / self.results['total']) * 100 if self.results['total'] > 0 else 0
        
        print("\n" + "="*80)
        print("🏁 BULK VOICE TEST RESULTS")
        print("="*80)
        print(f"⏱️  Duration: {duration:.1f} seconds")
        print(f"📊 Total voices tested: {self.results['total']}")
        print(f"✅ Successful: {success_count}")
        print(f"❌ Failed: {failed_count}")
        print(f"📈 Success rate: {success_rate:.1f}%")
        print(f"⚡ Average speed: {self.results['total']/duration:.1f} voices/second")
        
        if self.results['success']:
            total_size = sum(r.get('file_size', 0) for r in self.results['success'])
            avg_size = total_size / len(self.results['success'])
            print(f"💾 Average file size: {avg_size:.0f} bytes")
        
        # Show failed voices if any
        if self.results['failed']:
            print(f"\n❌ FAILED VOICES ({failed_count}):")
            print("-" * 60)
            for result in self.results['failed']:
                voice = result['voice']
                error = result['error']
                print(f"   {voice['short_name']} ({voice['locale']}) - {error}")
        
        # Show language breakdown
        if self.results['success']:
            print(f"\n📊 SUCCESS BY LANGUAGE:")
            print("-" * 40)
            lang_count = {}
            for result in self.results['success']:
                lang = result['voice']['language']
                lang_count[lang] = lang_count.get(lang, 0) + 1
            
            for lang, count in sorted(lang_count.items()):
                print(f"   {lang}: {count} voices")
        
        print("="*80)

async def main():
    """Main function for bulk testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Bulk Voice Tester for TTS')
    parser.add_argument('--save-audio', action='store_true', 
                       help='Save audio files for each voice (creates voice_samples directory)')
    parser.add_argument('--language', '-l', type=str, 
                       help='Test only voices for specific language (e.g., "en", "zh", "es")')
    parser.add_argument('--concurrent', '-c', type=int, default=5,
                       help='Maximum concurrent voice tests (default: 5)')
    parser.add_argument('--quick', '-q', action='store_true',
                       help='Quick test (first 20 voices only)')
    
    args = parser.parse_args()
    
    tester = BulkVoiceTester()
    
    if args.quick:
        print("🏃 Quick test mode - testing first 20 voices only")
        tester.tts.voices = tester.tts.voices[:20]
    
    if args.language:
        await tester.test_by_language(args.language, args.save_audio)
    else:
        await tester.test_all_voices(args.save_audio, args.concurrent)

if __name__ == "__main__":
    asyncio.run(main()) 