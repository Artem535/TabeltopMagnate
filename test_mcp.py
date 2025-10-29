from fastmcp import FastMCP

server = FastMCP(name="test")

@server.tool
def sum(a: int, b: int) -> int:
    """
    Add two numbers
    :param a: First number
    :param b: Second number
    :return: The sum of two numbers.
    """
    return a + b

if __name__ == "__main__":
    server.run("http", port = 8000)