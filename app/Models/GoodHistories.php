<?php

namespace App\Models;

use Backpack\CRUD\app\Models\Traits\CrudTrait;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class GoodHistories extends Model
{
    use CrudTrait;
    use HasFactory;

    protected $table = 'good_histories';
    protected $guarded = ['id'];
    protected $fillable = [
        'title',
        'description',
        'user_id',
        'is_moderated',
        'image',
    ];

    public function user()
    {
        return $this->belongsTo(User::class);
    }

    public function tags()
    {
        return $this->belongsToMany(Tags::class, 'good_histories_tags', 'good_history_id', 'tag_id');
    }
}