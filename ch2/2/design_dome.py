import math

GRAVITY_MARS = 0.38

sphere_results = []


def sphere_area(diameter, material, thickness):
    densities = {'glass': 2.4, 'aluminum': 2.7, 'carbon_steel': 7.85}
    density = densities[material]

    radius = diameter / 2
    area = 2 * math.pi * radius ** 2
    thickness_m = thickness / 100  # cm → m
    volume = area * thickness_m

    density = densities[material] * 1000
    mass = volume * density
    weight_on_mars = mass * GRAVITY_MARS

    area_rounded = round(area, 3)
    weight_rounded = round(weight_on_mars, 3)

    result = {
            '재질': material,
            '지름': diameter,
            '두께': thickness,
            '면적': area_rounded,
            '무게': weight_rounded
        }

    sphere_results.append(result)

    print(f'재질 ⇒ {material}, 지름 ⇒ {diameter}, 두께 ⇒ {thickness}\
          , 면적 ⇒ {area_rounded}, 무게 ⇒ {weight_rounded} kg')


def main():
    try:
        while True:
            user_input = input(
                'Input diameter and material(glass, aluminum, carbon_steel)\
                     and thickness(default = 1.0): ')

            if user_input[0] == 'exit':
                break

            data = user_input.strip().split()

            if len(data) < 2:
                raise ValueError

            diameter = float(data[0])
            material = data[1]
            thickness = 1.0
            if len(data) == 3:
                thickness = float(data[2])

            sphere_area(diameter, material, thickness)

    except ValueError:
        print('invalid input.')

    except KeyError:
        print('invalid material.')

    except IndexError:
        print('invalid input.')

    except KeyboardInterrupt:
        print()


if __name__ == '__main__':
    main()
