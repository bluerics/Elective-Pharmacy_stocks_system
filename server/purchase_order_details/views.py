from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import PurchaseOrderDetail
from .serializers import PurchaseOrderDetailSerializer
from rest_framework.permissions import IsAuthenticated


class PurchaseOrderDetailView(APIView):
    permission_classes=[IsAuthenticated]

    def get_object(self, pk):

        try:

            return PurchaseOrderDetail.objects.get(pk=pk)

        except PurchaseOrderDetail.DoesNotExist:

            return None


    def get(self, request, pk=None):

        if pk is not None:

            detail = self.get_object(pk)

            if detail is None:

                return Response(
                    {
                        "message":
                        "Purchase order detail not found."
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = PurchaseOrderDetailSerializer(detail)

            return Response(serializer.data)


        details = PurchaseOrderDetail.objects.all()

        serializer = PurchaseOrderDetailSerializer(
            details,
            many=True
        )

        return Response(serializer.data)


    def post(self, request):

        serializer = PurchaseOrderDetailSerializer(
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

        detail = self.get_object(pk)

        if detail is None:

            return Response(
                {
                    "message":
                    "Purchase order detail not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = PurchaseOrderDetailSerializer(
            detail,
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

        detail = self.get_object(pk)

        if detail is None:

            return Response(
                {
                    "message":
                    "Purchase order detail not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = PurchaseOrderDetailSerializer(
            detail,
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

        if request.user.role != "ADMIN":
            return Response(
                {
                    "message": "Only Admin can delete purchase order detail."

                },
                status=status.HTTP_403_FORBIDDEN
            )

        detail = self.get_object(pk)

        if detail is None:

            return Response(
                {
                    "message":
                    "Purchase order detail not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        detail.delete()

        return Response(
            {
                "message":
                "Purchase order detail deleted successfully."
            },
            status=status.HTTP_204_NO_CONTENT
        )