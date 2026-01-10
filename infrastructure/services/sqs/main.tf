module "events_queue" {
  source = "../../modules/sqs_queue"

  name       = "${var.queue_name_prefix}_events_queue"
  fifo_queue = true
}

module "posts_queue" {
  source = "../../modules/sqs_queue"

  name       = "${var.queue_name_prefix}_posts_queue"
  fifo_queue = true
}
