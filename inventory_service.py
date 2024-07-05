import grpc
from concurrent import futures
import inventory_pb2
import inventory_pb2_grpc
import csv
import os

class InventoryService(inventory_pb2_grpc.InventoryServiceServicer):
    def __init__(self):
        self.products = {}
        self.load_products()

    def load_products(self):
        if os.path.exists('data/products.csv'):
            with open('data/products.csv', mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    self.products[int(row['id'])] = int(row['quantity'])

    def save_products(self):
        with open('data/products.csv', mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['id', 'name', 'quantity'])
            writer.writeheader()
            for product_id, quantity in self.products.items():
                writer.writerow({'id': product_id, 'quantity': quantity})

    def CheckAvailability(self, request, context):
        product_id = request.product_id
        required_qty = request.required_qty
        if product_id in self.products and self.products[product_id] >= required_qty:
            return inventory_pb2.CheckAvailabilityResponse(available=True)
        else:
            return inventory_pb2.CheckAvailabilityResponse(available=False)

    def UpdateInventory(self, request, context):
        product_id = request.product_id
        change_qty = request.change_qty
        if product_id in self.products:
            self.products[product_id] += change_qty
            self.save_products()
            return inventory_pb2.UpdateInventoryResponse(success=True)
        else:
            return inventory_pb2.UpdateInventoryResponse(success=False)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    inventory_pb2_grpc.add_InventoryServiceServicer_to_server(InventoryService(), server)
    server.add_insecure_port('[::]:50053')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
