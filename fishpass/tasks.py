# Create your tasks here
from __future__ import absolute_import, unicode_literals
# from celery import shared_task
#
#
# @shared_task
# def add(x, y):
#     return x + y
#
#
# @shared_task
# def mul(x, y):
#     return x * y
#
#
# @shared_task
# def xsum(numbers):
#     return sum(numbers)

# @shared_task
#RDH: This didn't work, so I stuffed the task directly into celery.py
def run_view(view, *args):
    # import fishpass
    # fishpass_view = None
    # for count, argument in enumarate(args):
    #     if callable(argument) and hasattr(fishpass.views, argument.__name__):
    #         fishpass_view = args.pop(count)
    #         break
    # if fishpass_view:
    return view(*args)
