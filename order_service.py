from concurrent import futures
import grpc
import order_pb2
import order_pb2_grpc
import csv
import os

class OrderService(order_pb2_grpc.OrderServiceServicer):
    def __init__(self):
        self.order_file = 'orders.csv'
        self.load_orders()

    def load_orders(self):
        self.orders = []
        if os.path.exists(self.order_file):
            with open(self.order_file, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    self.orders.append(order_pb2.Order(
                        id=int(row['id']),
                        product_id=int(row['product_id']),
                        order_qty=int(row['order_qty'])
                    ))

    def save_orders(self):
        with open(self.order_file, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['id', 'product_id', 'order_qty'])
            writer.writeheader()
            for order in self.orders:
                writer.writerow({'id': order.id, 'product_id': order.product_id, 'order_qty': order.order_qty})

    def CreateOrder(self, request, context):
        order = request.order
        order.id = len(self.orders) + 1
        self.orders.append(order)
        self.save_orders()
        return order_pb2.CreateOrderResponse(order=order)

    def ListOrders(self, request, context):
        return order_pb2.ListOrdersResponse(orders=self.orders)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    order_pb2_grpc.add_OrderServiceServicer_to_server(OrderService(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
