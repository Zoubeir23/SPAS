# Serializers à créer/mettre à jour

## 1. Students (apps/students/serializers.py)
- StudentSerializer (complet avec relations)
- StudentListSerializer (minimal pour listes)
- StudentCreateSerializer (création/modification)

## 2. Programs (apps/programs/serializers.py)
- ProgramSerializer (complet)
- ProgramListSerializer (minimal)
- ProgramCreateSerializer (création)
- SubjectSerializer (complet)
- SubjectListSerializer (minimal)
- SubjectCreateSerializer (création)

## 3. Sessions (apps/sessions/serializers.py)
- SessionSerializer (complet)
- SessionListSerializer (minimal)
- SessionCreateSerializer (création)

## 4. Grades (apps/grades/serializers.py)
- GradeSerializer (complet)
- GradeListSerializer (minimal)
- GradeCreateSerializer (création)
- GradeBulkCreateSerializer (création multiple)

## 5. Attendance (apps/attendance/serializers.py)
- AttendanceSerializer (complet)
- AttendanceListSerializer (minimal)
- AttendanceCreateSerializer (création)
- AttendanceBulkCreateSerializer (création multiple)

## 6. Predictions (apps/predictions/serializers.py)
- PredictionSerializer (complet)
- PredictionListSerializer (minimal)
- PredictionCreateSerializer (création)
- RecommendedInterventionSerializer

## 7. Alerts (apps/alerts/serializers.py)
- AlertSerializer (complet)
- AlertListSerializer (minimal)
- AlertCreateSerializer (création)
- AlertActionSerializer

## 8. ML (apps/ml/serializers.py)
- MLModelSerializer (complet)
- MLModelListSerializer (minimal)
- TrainingJobSerializer

## 9. Users (apps/users/serializers.py)
- UserSerializer (complet)
- UserListSerializer (minimal)
- UserCreateSerializer (création)
- ChangePasswordSerializer
