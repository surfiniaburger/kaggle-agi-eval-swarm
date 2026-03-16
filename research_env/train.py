def count_triangles(sides):
    """
    Counts the number of triangles in a given set of sides.

    Args:
        sides: A list of integers representing the sides of the triangle.

    Returns:
        The number of triangles that can be formed from the given sides.
    """
    import math
    if len(sides) < 3:
        return 0
    
    count = 0
    for i in range(len(sides)):
        for j in range(i + 1, len(sides)):
            for k in range(j + 1, len(sides)):
                a, b, c = sides[i], sides[j], sides[k]
                if a + b > c and a + c > b and b + c > a:
                    count += 1
    return count

if __name__ == '__main__':
    # Get the number of sides from the user
    sides = int(input())
    
    # Calculate the number of triangles
    num_triangles = count_triangles(sides)
    
    # Print the result
    print(num_triangles)