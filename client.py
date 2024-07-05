import grpc
import product_pb2
import product_pb2_grpc
import order_pb2
import order_pb2_grpc
import inventory_pb2
import inventory_pb2_grpc
from tabulate import tabulate

def run():
    product_channel = grpc.insecure_channel('localhost:50051')
    product_stub = product_pb2_grpc.ProductServiceStub(product_channel)

    order_channel = grpc.insecure_channel('localhost:50052')
    order_stub = order_pb2_grpc.OrderServiceStub(order_channel)

    inventory_channel = grpc.insecure_channel('localhost:50053')
    inventory_stub = inventory_pb2_grpc.InventoryServiceStub(inventory_channel)

    while True:
        print("\nSelect an option:")
        print("1. Insert Product")
        print("2. Create Order")
        print("3. View All Products")
        print("4. View All Orders")
        print("5. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            name = input("Enter product name: ")
            quantity = int(input("Enter product quantity: "))
            product = product_pb2.Product(name=name, quantity=quantity)
            response = product_stub.CreateProduct(product_pb2.CreateProductRequest(product=product))
            print(f"Product created: {response.product}")

        elif choice == "2":
            product_id = int(input("Enter product ID: "))
            order_qty = int(input("Enter order quantity: "))
            response = inventory_stub.CheckAvailability(inventory_pb2.CheckAvailabilityRequest(product_id=product_id, required_qty=order_qty))
            if response.available:
                order = order_pb2.Order(id=0, product_id=product_id, order_qty=order_qty)
                order_response = order_stub.CreateOrder(order_pb2.CreateOrderRequest(order=order))
                print(f"Order created: {order_response.order}")
                inventory_stub.UpdateInventory(inventory_pb2.UpdateInventoryRequest(product_id=product_id, change_qty=-order_qty))
            else:
                print("Insufficient product quantity")

        elif choice == "3":
            response = product_stub.ListProducts(product_pb2.ListProductsRequest())
            products = [(p.id, p.name, p.quantity) for p in response.products]
            headers = ["ID", "Name", "Quantity"]
            print(tabulate(products, headers, tablefmt="grid"))

        elif choice == "4":
            response = order_stub.ListOrders(order_pb2.ListOrdersRequest())
            orders = [(o.id, o.product_id, o.order_qty) for o in response.orders]
            headers = ["Order ID", "Product ID", "Quantity"]
            print(tabulate(orders, headers, tablefmt="grid"))

        elif choice == "5":
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    run()
