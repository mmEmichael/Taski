from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


cancel_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Отменить", callback_data="cancel_create_task")]
    ]
)


create_task_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Создать задачу"),
            KeyboardButton(text="Задачи")
        ],
    ],
    resize_keyboard=True,
)


def delete_task_inline_kb(task_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Удалить🗑️",
                    callback_data=f"delete_task:{task_id}",
                ),
                InlineKeyboardButton(
                    text="Иноформация",
                    callback_data=f"task_info:{task_id}",
                )
            ]
        ]
    )