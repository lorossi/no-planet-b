import argparse

from canvas import Canvas


def main(args) -> None:
    # create a canvas
    canvas = Canvas(args.size, args.title_size, args.border)

    # load data according to the args
    if args.static:
        canvas.loadYears()
    else:
        canvas.loadMonths()

    # init the squares
    canvas.createSquares()

    if args.static:
        filename = "output/all.png"
        print("Generating one frame")
        canvas.draw()
        canvas.save(filename)
    else:
        # draw each frame separately
        for frame in range(args.duration):
            filename = f"output/frames/{str(frame).zfill(7)}.png"
            print(f"Generating frame {frame + 1}/{args.duration}")
            canvas.draw(frame, args.duration)
            canvas.save(filename)

            if args.debug:
                break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Creates the animation")
    parser.add_argument(
        "-d",
        "--duration",
        type=int,
        help="destination video duration in frames (defaults to 1080)",
        default=1080,
    )
    parser.add_argument(
        "-s",
        "--size",
        type=int,
        help="size of the animation (defaults to 1000px)",
        default=1000,
    )
    parser.add_argument(
        "-t",
        "--title-size",
        type=int,
        help="size of the title (defaults to 80px)",
        default=80,
    )
    parser.add_argument(
        "-b",
        "--border",
        type=float,
        help="border ration (defaults to 0.1)",
        default=0.1,
    )

    parser.add_argument(
        "-S",
        "--static",
        help="Generate a static image of the average temperature for all years",
        action="store_true",
    )
    parser.add_argument(
        "--debug", help="debug by saving the first frame only", action="store_true"
    )

    args = parser.parse_args()
    main(args)
