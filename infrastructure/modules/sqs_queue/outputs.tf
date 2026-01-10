output "queue" {
  value = aws_sqs_queue.queue
}

output "queue_url" {
  value = aws_sqs_queue.queue.url
}

output "queue_arn" {
  value = aws_sqs_queue.queue.arn
}

output "deadletter_queue" {
  value = aws_sqs_queue.deadletter_queue
}

output "deadletter_queue_url" {
  value = aws_sqs_queue.deadletter_queue.url
}

output "deadletter_queue_arn" {
  value = aws_sqs_queue.deadletter_queue.arn
}