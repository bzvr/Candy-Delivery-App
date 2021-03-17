from rest_framework.views import exception_handler

CLASS_NAME = {"CourierView": ("courier_id", "couriers"), "NewOrderView": ("order_id", "orders")}


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.

    response = exception_handler(exc, context)

    sid, name = CLASS_NAME[context['view'].__class__.__name__]

    if response is not None:
        customized_response = {'validation_error': {name: []}}
        for i, obj in enumerate(response.data):
            if obj:
                oid = context['request'].data['data'][i][sid]
                error = {'id': oid, 'errors': []}
                for key, value in obj.items():
                    error['errors'].append({"field": key, "message": value})
                customized_response["validation_error"][name].append(error)

        response.data = customized_response
    return response
