from PIL import Image, ImageDraw, ImageColor


class RMap:

    def __init__(self, scaling=100):
        self.white = ImageColor.getrgb('#ffffff')
        self.black = ImageColor.getrgb('#000000')
        self.blue = ImageColor.getrgb('#42B2E6')
        self.purple = ImageColor.getrgb('#9666F5')

        self.enable = ImageColor.getrgb('#B3B3B3')
        self.disable = ImageColor.getrgb('#D9D9D9')

        self.img_dim = (0, 0)
        self.scaling = scaling

        self.img = Image.new('RGB', self.img_dim, color=self.white)

    def draw_rect(self, x_pos, y_pos, x_dim, y_dim, name, color):
        """
        Draw a rectangle
        :param x_pos: x position of the rectangle
        :param y_pos: y position of the rectangle
        :param x_dim: x dimension of the rectangle
        :param y_dim: y dimension of the rectangle
        :param name: name of the rectangle
        :param color: color for the background
        :return: nothing
        """
        x1 = int(x_pos * self.scaling)
        x2 = int((x_pos + x_dim) * self.scaling)
        y1 = int(y_pos * self.scaling)
        y2 = int((y_pos + y_dim) * self.scaling)

        if x2 > self.img_dim[0] or y2 > self.img_dim[1]:
            x_more = 0
            y_more = 0
            if self.img_dim[0] < x2:
                x_more = x2 - self.img_dim[0]
            if self.img_dim[1] < y2:
                y_more = y2 - self.img_dim[1]
            self.enlarge(x_more, y_more)

        draw = ImageDraw.Draw(self.img)
        draw.rectangle((x1, y1, x2, y2), fill=color)

        draw.text((x1+5, y1+5), name, fill=self.white)

    def add_table(self, x_pos, y_pos, x_dim=1, y_dim=1, name='Table'):
        """
        Adds a table to the image
        :param x_pos: x position of the table
        :param y_pos: y position of the table
        :param x_dim: x dimension of the table
        :param y_dim: y dimension of the table
        :param name: name of the table
        :return: nothing
        """
        self.draw_rect(x_pos, y_pos, x_dim, y_dim, name, color=self.blue)

    def add_seat(self, x_pos, y_pos, seat_dim, name='Seat', enable=True):
        """
        Adds a seat to the image
        :param x_pos: x position of the seat
        :param y_pos: y position of the seat
        :param seat_dim: dimension of the seat
        :param name: name of the seat
        :param enable: boolean to indicate if the seat is enables or not
        :return: nothing
        """
        if enable:
            self.draw_rect(x_pos, y_pos, seat_dim, seat_dim, name, color=self.enable)
        else:
            self.draw_rect(x_pos, y_pos, seat_dim, seat_dim, name, color=self.disable)

    def enlarge(self, x_more, y_more):
        """
        Utility function to enlarge the canvas if new elements should be inserted.
        :param x_more: pixels to add to the canvas to  the x axis
        :param y_more: pixels to add to the canvas to  the y axis
        :return: nothing
        """
        self.img_dim = (self.img_dim[0] + x_more, self.img_dim[1] + y_more)
        img_temp = Image.new('RGB', self.img_dim, color=self.white)
        img_temp.paste(self.img, (0, 0))
        self.img = img_temp

    def show(self, run_number, solution_idx):
        """
        Shows the image in a computer window
        :param run_number: Identifier of the run session of the program
        :param solution_idx: Identifies of the solution
        :return: nothing
        """
        self.img.show(title=f'{run_number}-{solution_idx}')

    def save(self, run_number, solution_idx):
        """
        Save the image to the output folder
        :param run_number: Identifier of the run session of the program
        :param solution_idx: Identifies of the solution
        :return: nothing
        """
        self.img.save(f'output/{run_number}-{solution_idx}.png')
