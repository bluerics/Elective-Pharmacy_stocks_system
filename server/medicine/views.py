from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Medicine
from .serializers import MedicineSerializer
from rest_framework.permissions import IsAuthenticated


class MedicineView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):

        try:
            return Medicine.objects.get(pk=pk)

        except Medicine.DoesNotExist:
            return None


    def get(self, request, pk=None):

        if pk is not None:

            medicine = self.get_object(pk)

            if medicine is None:

                return Response(
                    {
                        "message":
                        "Medicine not found."
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = MedicineSerializer(medicine)

            return Response(serializer.data)


        medicines = Medicine.objects.all()

        serializer = MedicineSerializer(
            medicines,
            many=True
        )

        return Response(serializer.data)


    def post(self, request):

        serializer = MedicineSerializer(
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

        medicine = self.get_object(pk)

        if medicine is None:

            return Response(
                {
                    "message":
                    "Medicine not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = MedicineSerializer(
            medicine,
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

        medicine = self.get_object(pk)

        if medicine is None:

            return Response(
                {
                    "message":
                    "Medicine not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = MedicineSerializer(
            medicine,
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
                    "message": "Only ADMIN can delete medicines."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        medicine = self.get_object(pk)

        if medicine is None:
            return Response(
                {
                    "message": "Medicine not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        medicine.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )