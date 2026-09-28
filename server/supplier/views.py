from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Supplier
from .serializers import SupplierSerializer


class SupplierView(APIView):

    def get_object(self, pk):

        try:

            return Supplier.objects.get(pk=pk)

        except Supplier.DoesNotExist:

            return None


    def get(self, request, pk=None):

        if pk is not None:

            supplier = self.get_object(pk)

            if supplier is None:

                return Response(
                    {
                        "message":
                        "Supplier not found."
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = SupplierSerializer(supplier)

            return Response(serializer.data)


        suppliers = Supplier.objects.all()

        serializer = SupplierSerializer(
            suppliers,
            many=True
        )

        return Response(serializer.data)


    def post(self, request):

        serializer = SupplierSerializer(
            data=request.data
        )

        if serializer.is_valid():

            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


    def put(self, request, pk):

        supplier = self.get_object(pk)

        if supplier is None:

            return Response(
                {
                    "message":
                    "Supplier not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = SupplierSerializer(
            supplier,
            data=request.data
        )

        if serializer.is_valid():

            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


    def patch(self, request, pk):

        supplier = self.get_object(pk)

        if supplier is None:

            return Response(
                {
                    "message":
                    "Supplier not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = SupplierSerializer(
            supplier,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():

            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


    def delete(self, request, pk):

        supplier = self.get_object(pk)

        if supplier is None:

            return Response(
                {
                    "message":
                    "Supplier not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        supplier.delete()

        return Response(
            {
                "message":
                "Supplier deleted successfully."
            },
            status=status.HTTP_204_NO_CONTENT
        )