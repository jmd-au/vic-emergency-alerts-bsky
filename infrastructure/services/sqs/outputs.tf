output "events_queue_url" {
  value = module.events_queue.queue_url
}

output "events_queue_arn" {
  value = module.events_queue.queue_arn
}

output "posts_queue_url" {
  value = module.posts_queue.queue_url
}

output "posts_queue_arn" {
  value = module.posts_queue.queue_arn
}
