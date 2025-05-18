<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Reconstruction extends Model
{
    use HasFactory;

    protected $fillable = [
        'timestamp',
        'is_saved',
        'is_processing',
        'is_model_ready',
        'is_failed',
        'message',
    ];

    protected $casts = [
        'is_saved' => 'boolean',
        'is_processing' => 'boolean',
        'is_model_ready' => 'boolean',
        'is_failed' => 'boolean',
    ];
}
