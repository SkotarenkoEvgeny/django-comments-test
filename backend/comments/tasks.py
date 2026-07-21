from celery import shared_task


@shared_task
def test_task(comment_id):
    print(
        f"CELERY TASK: New comment ID = {comment_id}",
        flush=True,
    )
