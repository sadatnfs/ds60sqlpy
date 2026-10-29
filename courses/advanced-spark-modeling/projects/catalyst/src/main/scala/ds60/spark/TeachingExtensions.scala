package ds60.spark

import org.apache.spark.sql.SparkSessionExtensions
import org.apache.spark.sql.catalyst.FunctionIdentifier
import org.apache.spark.sql.catalyst.analysis.TypeCheckResult
import org.apache.spark.sql.catalyst.expressions.{Expression, ExpressionInfo, UnaryExpression}
import org.apache.spark.sql.catalyst.expressions.codegen.{CodegenContext, ExprCode}
import org.apache.spark.sql.catalyst.plans.logical.LogicalPlan
import org.apache.spark.sql.catalyst.rules.Rule
import org.apache.spark.sql.types.{DataType, DoubleType, LongType}

// Original teaching expressions. This project targets Spark 4.0.1 exactly.
case class StableSoftplus(child: Expression) extends UnaryExpression {
  override def dataType: DataType = DoubleType
  override def prettyName: String = "teaching_softplus"
  override def checkInputDataTypes(): TypeCheckResult =
    if (child.dataType == DoubleType) TypeCheckResult.TypeCheckSuccess
    else TypeCheckResult.TypeCheckFailure("teaching_softplus requires DOUBLE; cast explicitly")
  override protected def nullSafeEval(value: Any): Any = {
    val z = value.asInstanceOf[Double]
    math.max(z, 0.0) + math.log1p(math.exp(-math.abs(z)))
  }
  override protected def doGenCode(ctx: CodegenContext, ev: ExprCode): ExprCode =
    nullSafeCodeGen(
      ctx,
      ev,
      z =>
        s"${ev.value} = java.lang.Math.max($z, 0.0d) + java.lang.Math.log1p(java.lang.Math.exp(-java.lang.Math.abs($z)));"
    )
  override protected def withNewChildInternal(next: Expression): StableSoftplus = copy(child = next)
}

case class ClipCount(child: Expression) extends UnaryExpression {
  override def dataType: DataType = LongType
  override def prettyName: String = "teaching_clip_count"
  override def checkInputDataTypes(): TypeCheckResult =
    if (child.dataType == LongType) TypeCheckResult.TypeCheckSuccess
    else TypeCheckResult.TypeCheckFailure("teaching_clip_count requires BIGINT")
  override protected def nullSafeEval(value: Any): Any = math.max(value.asInstanceOf[Long], 0L)
  override protected def doGenCode(ctx: CodegenContext, ev: ExprCode): ExprCode =
    nullSafeCodeGen(ctx, ev, x => s"${ev.value} = java.lang.Math.max($x, 0L);")
  override protected def withNewChildInternal(next: Expression): ClipCount = copy(child = next)
}

class CollapseClipCount extends Rule[LogicalPlan] {
  override def apply(plan: LogicalPlan): LogicalPlan = plan.transformAllExpressions {
    case ClipCount(inner: ClipCount) => inner
  }
}

class TeachingExtensions extends (SparkSessionExtensions => Unit) {
  override def apply(extensions: SparkSessionExtensions): Unit = {
    extensions.injectFunction(
      (
        FunctionIdentifier("teaching_softplus"),
        new ExpressionInfo(classOf[StableSoftplus].getName, "teaching_softplus"),
        (arguments: Seq[Expression]) => {
          require(arguments.size == 1, "teaching_softplus takes exactly one argument")
          StableSoftplus(arguments.head)
        }
      )
    )
    extensions.injectFunction(
      (
        FunctionIdentifier("teaching_clip_count"),
        new ExpressionInfo(classOf[ClipCount].getName, "teaching_clip_count"),
        (arguments: Seq[Expression]) => {
          require(arguments.size == 1, "teaching_clip_count takes exactly one argument")
          ClipCount(arguments.head)
        }
      )
    )
    extensions.injectOptimizerRule(_ => new CollapseClipCount)
  }
}
