import grpc
from concurrent import futures
import product_pb2
import product_pb2_grpc
import csv
import os

class ProductService(product_pb2_grpc.ProductServiceServicer):
    def __init__(self):
        self.products = {}
        self.load_products()

    def load_products(self):
        if os.path.exists('data/products.csv'):
            with open('data/products.csv', mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    self.products[int(row['id'])] = product_pb2.Product(id=int(row['id']), name=row['name'], quantity=int(row['quantity']))

    def save_products(self):
        with open('data/products.csv', mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['id', 'name', 'quantity'])
            writer.writeheader()
            for product in self.products.values():
                writer.writerow({'id': product.id, 'name': product.name, 'quantity': product.quantity})

    def get_next_product_id(self):
        if self.products:
            return max(self.products.keys()) + 1
        else:
            return 1

    def CreateProduct(self, request, context):
        product_id = self.get_next_product_id()
        new_product = product_pb2.Product(id=product_id, name=request.product.name, quantity=request.product.quantity)
        self.products[product_id] = new_product
        self.save_products()
        return product_pb2.CreateProductResponse(product=new_product)

    def GetProduct(self, request, context):
        product = self.products.get(request.id)
        if product:
            return product_pb2.GetProductResponse(product=product)
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Product not found')
            return product_pb2.GetProductResponse()

    def ListProducts(self, request, context):
        return product_pb2.ListProductsResponse(products=list(self.products.values()))

    def UpdateProduct(self, request, context):
        product = self.products.get(request.product.id)
        if product:
            self.products[request.product.id] = request.product
            self.save_products()
            return product_pb2.UpdateProductResponse(success=True)
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Product not found')
            return product_pb2.UpdateProductResponse(success=False)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    product_pb2_grpc.add_ProductServiceServicer_to_server(ProductService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
