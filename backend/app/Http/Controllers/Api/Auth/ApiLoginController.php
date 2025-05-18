<?php

namespace App\Http\Controllers\Api\Auth;

use App\Http\Controllers\Controller;
use Illuminate\Foundation\Auth\AuthenticatesUsers;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Validator;

class ApiLoginController extends Controller
{
    // use AuthenticatesUsers;
    public function login(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'email'    => 'required|email',
            'password' => 'required'
        ]);

        if ($validator->fails()) {
            return response()->json([
                'status' => 'error',
                'errors' => $validator->errors()
            ], 422);
        }

        $credentials = $request->only('email', 'password');

        if (!Auth::attempt($credentials)) {
            return response()->json([
                'status' => 'failed',
                'message' => 'Incorrect email or password'
            ], 401);
        }

        $user = Auth::user();
        $bearerToken = $user->createToken('authToken')->plainTextToken;
        return response()->json([
            'status' => 'success',
            'user' => $user,
            'token' => $bearerToken
        ]);
    }
}
