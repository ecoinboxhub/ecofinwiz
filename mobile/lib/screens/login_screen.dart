import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../config/theme.dart';
import '../providers/auth_provider.dart';
import 'register_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _formKey = GlobalKey<FormState>();
  bool _loading = false;
  bool _obscure = true;

  Future<void> _login() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _loading = true);
    try {
      await context.read<AuthProvider>().login(_emailController.text.trim(), _passwordController.text);
      if (mounted) Navigator.popUntil(context, (route) => route.isFirst);
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Login failed: $e')));
    }
    if (mounted) setState(() => _loading = false);
  }

  @override
  void dispose() { _emailController.dispose(); _passwordController.dispose(); super.dispose(); }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(child: SingleChildScrollView(padding: const EdgeInsets.all(24), child: Form(key: _formKey, child: Column(children: [
        const SizedBox(height: 40),
        Container(width: 56, height: 56, decoration: const BoxDecoration(gradient: LinearGradient(colors: AppColors.tealMintGradient), borderRadius: BorderRadius.all(Radius.circular(14))),
          child: const Center(child: Text('F', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 28)))),
        const SizedBox(height: 16),
        const Text('Welcome Back', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: AppTheme.ink)),
        const SizedBox(height: 4),
        const Text('Sign in to your account', style: TextStyle(color: AppTheme.muted)),
        const SizedBox(height: 32),
        TextFormField(controller: _emailController, decoration: const InputDecoration(labelText: 'Email', prefixIcon: Icon(Icons.email_outlined)), keyboardType: TextInputType.emailAddress, validator: (v) => v?.contains('@') == true ? null : 'Valid email required'),
        const SizedBox(height: 16),
        TextFormField(controller: _passwordController, decoration: InputDecoration(labelText: 'Password', prefixIcon: const Icon(Icons.lock_outlined), suffixIcon: IconButton(icon: Icon(_obscure ? Icons.visibility_off : Icons.visibility), onPressed: () => setState(() => _obscure = !_obscure))), obscureText: _obscure, validator: (v) => (v?.length ?? 0) >= 6 ? null : 'Min. 6 characters'),
        const SizedBox(height: 24),
        SizedBox(width: double.infinity, child: ElevatedButton(onPressed: _login, child: _loading ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white)) : const Text('Sign In'))),
        const SizedBox(height: 16),
        const Text('Google sign-in is coming soon. For now, please sign in with your email.',
            textAlign: TextAlign.center, style: TextStyle(color: AppTheme.softMuted, fontSize: 13)),
        const SizedBox(height: 16),
        TextButton(onPressed: () => Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => const RegisterScreen())), child: const Text("Don't have an account? Sign Up")),
      ])))),
    );
  }
}
