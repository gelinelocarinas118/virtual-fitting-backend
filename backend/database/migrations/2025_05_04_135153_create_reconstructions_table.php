<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('reconstructions', function (Blueprint $table) {
            $table->id();
            $table->string('timestamp')->unique();
            $table->boolean('is_saved')->default(false);         // images uploaded
            $table->boolean('is_processing')->default(false);    // sent to Flask
            $table->boolean('is_model_ready')->default(false);   // .obj ready
            $table->boolean('is_failed')->default(false);        // any failure
            $table->string('message')->nullable();               // optional error or info
            $table->unsignedSmallInteger('height_cm')->nullable(); // record height
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('reconstructions');
    }
};
