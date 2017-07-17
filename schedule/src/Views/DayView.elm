module Views.DayView exposing (dayView)

-- Local modules

import Messages exposing (Msg(..))
import Models exposing (Model, DayIso)
import Views.FilterView exposing (filterSidebar)


-- External modules

import Html exposing (Html, text, div, ul, li, span, i, h4)
import Html.Attributes exposing (class, classList, href)
import Html.Events exposing (onClick)


dayView : DayIso -> Model -> Html Msg
dayView dayIso model =
    div []
        [ filterSidebar model
        ]
