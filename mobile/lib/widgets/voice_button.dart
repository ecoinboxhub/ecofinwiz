import 'package:flutter/material.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'package:flutter_tts/flutter_tts.dart';
import '../config/theme.dart';

class VoiceButton extends StatefulWidget {
  final Function(String)? onTranscript;
  final String? speakText;
  final String languageCode;
  final double size;
  final Color? color;

  const VoiceButton({
    super.key,
    this.onTranscript,
    this.speakText,
    this.languageCode = 'en-NG',
    this.size = 20,
    this.color,
  });

  static const Map<String, String> languageNames = {
    'en-NG': 'English (Nigeria)',
    'ha-NG': 'Hausa',
    'yo-NG': 'Yoruba',
    'ig-NG': 'Igbo',
    'sw-KE': 'Swahili',
    'zu-ZA': 'Zulu',
    'xh-ZA': 'Xhosa',
    'af-ZA': 'Afrikaans',
    'am-ET': 'Amharic',
    'so-SO': 'Somali',
    'om-ET': 'Oromo',
    'ti-ET': 'Tigrinya',
    'ak-GH': 'Akan',
  };

  @override
  State<VoiceButton> createState() => _VoiceButtonState();
}

class _VoiceButtonState extends State<VoiceButton>
    with SingleTickerProviderStateMixin {
  stt.SpeechToText? _speech;
  FlutterTts? _tts;
  bool _isListening = false;
  bool _isSpeaking = false;
  late AnimationController _animController;

  static const Map<String, String> _sttLocales = {
    'en-NG': 'en_NG', 'ha-NG': 'ha_NG', 'yo-NG': 'yo_NG', 'ig-NG': 'ig_NG',
    'sw-KE': 'sw_KE', 'zu-ZA': 'zu_ZA', 'xh-ZA': 'xh_ZA', 'af-ZA': 'af_ZA',
    'am-ET': 'am_ET', 'so-SO': 'so_SO', 'om-ET': 'om_ET', 'ti-ET': 'ti_ET',
    'ak-GH': 'ak_GH',
  };

  static const Map<String, String> _ttsLocales = {
    'en-NG': 'en-NG', 'ha-NG': 'ha-NG', 'yo-NG': 'yo-NG', 'ig-NG': 'ig-NG',
    'sw-KE': 'sw-KE', 'zu-ZA': 'zu-ZA', 'xh-ZA': 'xh-ZA', 'af-ZA': 'af-ZA',
    'am-ET': 'am-ET', 'so-SO': 'so-SO', 'om-ET': 'om-ET', 'ti-ET': 'ti_ET',
    'ak-GH': 'ak-GH',
  };

  bool get _isMic => widget.onTranscript != null;

  @override
  void initState() {
    super.initState();
    _animController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 800),
    );
    if (widget.speakText != null) _initTts();
  }

  Future<bool> _initSpeech() async {
    try {
      _speech = stt.SpeechToText();
      final available = await _speech!.initialize(onError: (_) => _speechError());
      if (!available) {
        _speech = null;
        _speechError();
        return false;
      }
      return true;
    } catch (_) {
      _speech = null;
      _speechError();
      return false;
    }
  }

  Future<void> _initTts() async {
    try {
      _tts = FlutterTts();
    } catch (_) {}
  }

  Future<void> _toggleListening() async {
    if (_isListening) {
      await _speech?.stop();
      _animController.stop();
      if (mounted) setState(() => _isListening = false);
      return;
    }
    if (_speech == null) {
      final ok = await _initSpeech();
      if (!ok || !mounted || _speech == null) return;
      if (_speech?.isListening == true) return;
    }
    setState(() => _isListening = true);
    _animController.repeat(reverse: true);
    final locale = _sttLocales[widget.languageCode] ?? 'en_US';
    try {
      await _speech?.listen(
        localeId: locale,
        listenOptions: stt.SpeechListenOptions(cancelOnError: true, partialResults: true),
        onResult: (result) {
          setState(() {});
          if (result.finalResult && widget.onTranscript != null) {
            widget.onTranscript!(result.recognizedWords);
            _animController.stop();
            if (mounted) setState(() => _isListening = false);
          }
        },
      );
    } catch (_) {
      _speechError();
    }
  }

  void _speechError() {
    _animController.stop();
    if (!mounted) return;
    setState(() => _isListening = false);
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Microphone unavailable. Please allow microphone permission and try again.')),
    );
  }

  Future<void> _speak() async {
    if (_isSpeaking) return;
    if (_tts == null) await _initTts();
    if (_tts == null) return;
    setState(() => _isSpeaking = true);
    try {
      final locale = _ttsLocales[widget.languageCode] ?? 'en-US';
      await _tts!.setLanguage(locale);
      await _tts!.speak(widget.speakText ?? '');
      _tts!.setCompletionHandler(() {
        if (mounted) setState(() => _isSpeaking = false);
      });
    } catch (_) {
      if (mounted) setState(() => _isSpeaking = false);
    }
  }

  @override
  void dispose() {
    _speech?.stop();
    _tts?.stop();
    _animController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final defaultColor = widget.color ?? (_isMic ? AppTheme.primary : AppTheme.softMuted);

    if (_isMic) {
      return GestureDetector(
        onTap: _toggleListening,
        child: AnimatedBuilder(
          animation: _animController,
          builder: (context, child) {
            return Transform.scale(
              scale: _isListening ? 1.0 + _animController.value * 0.15 : 1.0,
              child: child,
            );
          },
          child: Icon(
            _isListening ? Icons.mic : Icons.mic_none,
            color: _isListening ? AppTheme.error : defaultColor,
            size: widget.size,
          ),
        ),
      );
    }

    return IconButton(
      visualDensity: VisualDensity.compact,
      icon: Icon(
        _isSpeaking ? Icons.volume_up : Icons.volume_up_outlined,
        color: _isSpeaking ? defaultColor : AppTheme.softMuted,
        size: widget.size,
      ),
      onPressed: _isSpeaking ? null : _speak,
    );
  }
}
